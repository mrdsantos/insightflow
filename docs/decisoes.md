# Decisoes de projeto

Registro curto das decisoes que alguem pode questionar depois. Uma secao por decisao,
com o porque e o que eu abriria mao se mudasse de ideia.

## Carga full refresh, nao incremental

Staging e dw (menos `dim_calendario`) sao truncados e recarregados a cada execucao do
pipeline. Com seed fixa e ~8k linhas, full refresh e deterministico, simples de auditar e
garante que rodar de novo apontando para o VPS reproduz tudo identico. Upsert incremental
seria mais codigo e mais estado para gerenciar sem nenhum ganho neste volume. Se o dataset
crescesse para milhoes de linhas, essa conta mudaria.

## metodo_pagamento e status_pedido como dimensoes degeneradas

Ficam como colunas texto no fato, nao como tabelas de dimensao. Cardinalidade minima
(4 e 5 valores), nenhum atributo proprio para carregar. Criar uma dim de 5 linhas e um
join a mais em toda consulta para nada. Se um dia status ganhasse atributos (ex.: etapa
do funil, SLA), viraria dimensao de verdade.

## Outlier de preco nao vai para quarentena

Quarentena e para registro invalido: dado quebrado, que nao da para interpretar. Preco
6x acima da faixa do produto e interpretavel - pode ser erro, pode ser variacao legitima
(edicao especial, bundle). Rejeitar seria decidir sem evidencia. O outlier permanece no
fato e a analise do bloco 2 (IQR vs z-score) decide como trata-lo estatisticamente.

## Coluna ID_Pedido alem do enunciado

O enunciado nao pede ID_Pedido, mas o gerador ja cria a coluna (1 a 5 itens por pedido,
com afinidades entre produtos). Motivo: uma analise de cesta de compras (market basket)
so faz sentido com nocao de pedido, e regenerar o dataset depois invalidaria fato, views
e analises ja commitadas. A coluna e inofensiva se o extra for cortado. E um desvio
consciente do enunciado, registrado aqui.

## Dev e producao na mesma instancia Postgres

O database `insightflow` local serve o desenvolvimento; o do VPS serve o dashboard
publicado. Sao instancias separadas, mas dentro de cada uma nao ha separacao dev/prod.
Atalho consciente para um desafio de fim de semana: o pipeline idempotente e quem garante
que qualquer ambiente reconstruido fica identico.

## Power BI fora do escopo

O enunciado aceita Power BI, Tableau ou bibliotecas Python. Fui de Streamlit + Plotly:
mantem todo o projeto em codigo versionavel, roda em container e publica como link
publico sem licenca. Power BI nao entra nem como export.

## Venda concretizada = Entregue + Enviado

Toda analise de receita e comportamento (KPIs, RFM, coorte, Pareto) considera venda o pedido
Entregue ou Enviado. Cancelado e Devolvido nao sao receita; Processando ainda pode virar
cancelamento, entao fica fora por conservadorismo. Enviado entra porque a mercadoria saiu e
a receita foi reconhecida - o risco de virar devolucao existe, mas o volume e pequeno e a
alternativa (so Entregue) descartaria venda legitima em transito. Analise no notebook 02.

## Churn com N = 90 dias

Cliente e considerado churned quando passa de 90 dias sem comprar. O numero sai dos dados:
o percentil 90 do intervalo entre compras consecutivas e 101 dias (notebook 02), e como os
KPIs sao mensais o corte precisa ser multiplo de mes cheio - 3 meses e o multiplo mais
proximo. Quem passa disso esta fora do ritmo de 9 em cada 10 recompras da base. Churn aqui
e operacional (cliente esfriou), nao definitivo: cliente pode voltar e reaparecer como ativo.

## Outlier marcado por IQR, nao z-score

Para marcar outliers na analise o criterio e IQR (1.5x alem do Q3). O z-score pressupoe
normalidade que a base nao tem (media de valor_unitario e 3x a mediana) e sofre de
mascaramento: media e desvio sao calculados com os proprios outliers dentro, o que empurra
o limite para cima. A comparacao numerica por categoria esta em `sql/consultas/q_outliers.sql`
e no notebook 02.

## Filtros do dashboard nao alcancam as views estruturais

RFM, coorte, Pareto, metricas por produto e share do top 10% sao calculados sobre a base
completa de vendas concretizadas e nao reagem aos filtros de categoria/UF/status. Quintil,
coorte e percentual acumulado so tem validade sobre a base inteira - recalcular por recorte
mudaria a pergunta respondida. Alem disso, `vw_crescimento_categoria` pre-calcula o MoM com
janela por categoria, entao aceita so filtro de periodo e categoria: cortar UF exigiria
recalcular a janela no app, e logica analitica nao roda no dashboard. Cada grafico estrutural
leva nota curta na interface.

## Filtro global na sidebar, nao por grafico

Uma unica barra de filtros para o dashboard inteiro, com estado preservado entre paginas
via `st.session_state`. Filtro dentro do card ou por pagina quebra a comparacao: dois
graficos passam a mostrar recortes diferentes sem avisar. E o mesmo padrao de Power BI e
Tableau, e atende o requisito de "filtros dinamicos para navegacao e comparacao": navegar
entre paginas mantendo o recorte e exatamente a comparacao. Os presets de periodo contam
a partir da ultima venda da base, nao do relogio - o dataset e um snapshot congelado e
"ultimos 30 dias" a partir de hoje retornaria vazio.

## Pareto sem eixo duplo

O Pareto classico poe barras de faturamento e linha de % acumulado em dois eixos Y, e o
alinhamento entre as duas escalas e arbitrario - inventa cruzamentos que nao existem nos
dados. Converti as barras para % do faturamento total: barras e linha passam a dividir a
mesma escala 0-100 e nenhuma informacao se perde. Eixo duplo esta banido do projeto
inteiro pelo mesmo motivo.

## Dispersao RFM com 3 cores e resto cinza

O RFM gera 10 segmentos nomeados, mas a dispersao destaca so Campeoes, Em Risco e
Perdidos; o resto fica cinza. Dispersao e forma par-a-par, onde o teto validado da paleta
e 3 series coloridas: com 10 cores haveria pares indistinguiveis sob daltonismo, e o
segmento que importa sumiria no meio. Destacar pouco e mais legivel e mais afiado
analiticamente. O mesmo principio vale para a matriz crescimento x faturamento de
produtos (maior volume, maior crescimento, maior queda).

## Tema claro fixo, sem modo escuro

A paleta foi validada (daltonismo e contraste) contra superficie clara. Modo escuro
exige uma segunda paleta com passos proprios validados contra a superficie escura - nao e
inversao automatica. Fora do escopo desta entrega por decisao, nao por esquecimento.
Toda cor do projeto vive em `app/theme.py` (template Plotly global) e
`.streamlit/config.toml`; nenhum grafico declara cor propria.

## O dashboard nao calcula nada em pandas

As paginas so aplicam filtro (equivalente de WHERE) e agregacao trivial (soma, contagem,
pivot). Janelas, quintis, percentuais acumulados e a definicao de churn vivem nas views
versionadas em `sql/views/`. Se um numero do dashboard divergir do SQL, o erro e do app,
nao da analise - e a view continua auditavel por quem nunca abriu o Python.

## Projecao usa a regressao mesmo com o baseline ganhando no teste

No split temporal (treino ate dez/2025, teste jan-jun/2026) a media movel de 3 meses
bateu a regressao por pouco: MAE 46,3k contra 51,9k, MAPE 18,9% contra 19,8%, R2 negativo
nos dois. Publiquei os numeros como sao - a tabela da pagina de Previsao mostra o baseline
vencendo. A projecao de jul-dez/2026, porem, sai da regressao: media movel realimentada
para frente converge para uma reta e nunca anteciparia o pico de novembro, que e o evento
mais importante do ano; a regressao carrega a dummy de novembro. Diferenca de 12% no MAE,
medida em 6 observacoes, nao justifica descartar o unico modelo com estrutura sazonal.
Analise completa no notebook 03.

## Seed fixa no gerador

`random.Random(SEED)` com seed constante no codigo. Duas execucoes geram o mesmo CSV
byte a byte, o que torna o dataset commitado reproduzivel por qualquer avaliador e faz
da carga remota uma reproducao exata da local, nao um retrabalho.

## Arquivos de view com prefixo numerico

`sql/views/` seguia a convencao de um arquivo por view com o nome da view, e o
`scripts/migrate.py` aplicava tudo em ordem alfabetica. So que `vw_vendas` e a base de que
onze das doze views leem, e `vw_vendas.sql` era o ultimo nome do alfabeto: o primeiro arquivo
aplicado ja fazia `FROM dw.vw_vendas`. Isso nunca falhou aqui porque o banco local ganhou as
views uma a uma ao longo dos blocos 2 a 4, e reaplicar `CREATE OR REPLACE` sobre view que ja
existe funciona. Em banco zerado - a VPS, o `docker compose` com volume novo, o avaliador
clonando o repo - quebrava sempre.

Adotei o prefixo numerico que `sql/ddl/` ja usava, agora refletindo a ordem de dependencia
entre as views. O `sorted()` do migrate continua sendo a unica regra de ordenacao, sem codigo
novo. A alternativa era manter os nomes e listar a ordem dentro do `migrate.py`, mas ai uma
view nova que ficasse de fora da lista seria ignorada em silencio, falha pior que a original,
que ao menos estourava. `tests/test_ordem_views.py` le os arquivos na mesma ordem do migrate
e falha se alguma view referenciar outra ainda nao criada.

## Titulo ancorado no container, faixa superior de 76px

Com `margin.t = 48`, o titulo (que por padrao se centra no meio da margem superior) e a legenda
horizontal (ancorada logo acima da area de plotagem) disputavam a mesma faixa de pixels e se
sobrepunham nos cinco graficos com legenda. Passei o titulo para `yref="container"` com
`yanchor="top"`, o que o prende ao topo da figura independentemente da altura da margem, e abri a
faixa superior para 76px - o suficiente para titulo e legenda empilhados.

A margem maior vale para todo grafico, inclusive os sem legenda. Aumentar so onde ha legenda
economizaria espaco em branco, mas desalinharia as areas de plotagem de graficos lado a lado
(na Home, sazonalidade tem legenda e categorias nao, e as duas dividem a mesma linha). Alinhamento
entre paineis vizinhos vale mais que 28px de altura.

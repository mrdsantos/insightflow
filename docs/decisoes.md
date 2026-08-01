# Decisões de projeto

Registro curto das decisões que alguém pode questionar depois. Uma seção por decisão,
com o porquê e o que eu abriria mão se mudasse de ideia.

## Carga full refresh, não incremental

Staging e dw (menos `dim_calendario`) são truncados e recarregados a cada execução do
pipeline. Com seed fixa e ~8k linhas, full refresh é determinístico, simples de auditar e
garante que rodar de novo apontando para o VPS reproduz tudo idêntico. Upsert incremental
seria mais código e mais estado para gerenciar sem nenhum ganho neste volume. Se o dataset
crescesse para milhões de linhas, essa conta mudaria.

## metodo_pagamento e status_pedido como dimensões degeneradas

Ficam como colunas texto no fato, não como tabelas de dimensão. Cardinalidade mínima
(4 e 5 valores), nenhum atributo próprio para carregar. Criar uma dim de 5 linhas é um
join a mais em toda consulta para nada. Se um dia status ganhasse atributos (ex.: etapa
do funil, SLA), viraria dimensão de verdade.

## Outlier de preço não vai para quarentena

Quarentena é para registro inválido: dado quebrado, que não dá para interpretar. Preço
6x acima da faixa do produto é interpretável - pode ser erro, pode ser variação legítima
(edição especial, bundle). Rejeitar seria decidir sem evidência. O outlier permanece no
fato e a análise do bloco 2 (IQR vs z-score) decide como tratá-lo estatisticamente.

## Coluna ID_Pedido além do enunciado

O enunciado não pede ID_Pedido, mas o gerador já cria a coluna (1 a 5 itens por pedido,
com afinidades entre produtos). Motivo: uma análise de cesta de compras (market basket)
só faz sentido com noção de pedido, e regenerar o dataset depois invalidaria fato, views
e análises já commitadas. A coluna é inofensiva se o extra for cortado. É um desvio
consciente do enunciado, registrado aqui.

## Dev e produção na mesma instância Postgres

O database `insightflow` local serve o desenvolvimento; o do VPS serve o dashboard
publicado. São instâncias separadas, mas dentro de cada uma não há separação dev/prod.
Atalho consciente para um desafio de fim de semana: o pipeline idempotente é quem garante
que qualquer ambiente reconstruído fica idêntico.

## Power BI fora do escopo

O enunciado aceita Power BI, Tableau ou bibliotecas Python. Fui de Streamlit + Plotly:
mantém todo o projeto em código versionável, roda em container e publica como link
público sem licença. Power BI não entra nem como export.

## Venda concretizada = Entregue + Enviado

Toda análise de receita e comportamento (KPIs, RFM, coorte, Pareto) considera venda o pedido
Entregue ou Enviado. Cancelado e Devolvido não são receita; Processando ainda pode virar
cancelamento, então fica fora por conservadorismo. Enviado entra porque a mercadoria saiu e
a receita foi reconhecida - o risco de virar devolução existe, mas o volume é pequeno e a
alternativa (só Entregue) descartaria venda legítima em trânsito. Análise no notebook 02.

## Churn com N = 90 dias

Cliente é considerado churned quando passa de 90 dias sem comprar. O número sai dos dados:
o percentil 90 do intervalo entre compras consecutivas é 101 dias (notebook 02), e como os
KPIs são mensais o corte precisa ser múltiplo de mês cheio - 3 meses é o múltiplo mais
próximo. Quem passa disso está fora do ritmo de 9 em cada 10 recompras da base. Churn aqui
é operacional (cliente esfriou), não definitivo: cliente pode voltar e reaparecer como ativo.

## Outlier marcado por IQR, não z-score

Para marcar outliers na análise o critério é IQR (1.5x além do Q3). O z-score pressupõe
normalidade que a base não tem (média de valor_unitario é 3x a mediana) e sofre de
mascaramento: média e desvio são calculados com os próprios outliers dentro, o que empurra
o limite para cima. A comparação numérica por categoria está em `sql/consultas/q_outliers.sql`
e no notebook 02.

## Filtros do dashboard não alcançam as views estruturais

RFM, coorte, Pareto, métricas por produto e share do top 10% são calculados sobre a base
completa de vendas concretizadas e não reagem aos filtros de categoria/UF/status. Quintil,
coorte e percentual acumulado só têm validade sobre a base inteira - recalcular por recorte
mudaria a pergunta respondida. Além disso, `vw_crescimento_categoria` pré-calcula o MoM com
janela por categoria, então aceita só filtro de período e categoria: cortar UF exigiria
recalcular a janela no app, e lógica analítica não roda no dashboard. Cada gráfico estrutural
leva nota curta na interface.

## Filtro global na sidebar, não por gráfico

Uma única barra de filtros para o dashboard inteiro, com estado preservado entre páginas
via `st.session_state`. Filtro dentro do card ou por página quebra a comparação: dois
gráficos passam a mostrar recortes diferentes sem avisar. É o mesmo padrão de Power BI e
Tableau, e atende o requisito de "filtros dinâmicos para navegação e comparação": navegar
entre páginas mantendo o recorte é exatamente a comparação. Os presets de período contam
a partir da última venda da base, não do relógio - o dataset é um snapshot congelado e
"últimos 30 dias" a partir de hoje retornaria vazio.

## Pareto sem eixo duplo

O Pareto clássico põe barras de faturamento e linha de % acumulado em dois eixos Y, e o
alinhamento entre as duas escalas é arbitrário - inventa cruzamentos que não existem nos
dados. Converti as barras para % do faturamento total: barras e linha passam a dividir a
mesma escala 0-100 e nenhuma informação se perde. Eixo duplo está banido do projeto
inteiro pelo mesmo motivo.

## Dispersão RFM com 3 cores e resto cinza

O RFM gera 10 segmentos nomeados, mas a dispersão destaca só Campeões, Em Risco e
Perdidos; o resto fica cinza. Dispersão é forma par-a-par, onde o teto validado da paleta
é 3 séries coloridas: com 10 cores haveria pares indistinguíveis sob daltonismo, e o
segmento que importa sumiria no meio. Destacar pouco é mais legível e mais afiado
analiticamente. O mesmo princípio vale para a matriz crescimento x faturamento de
produtos (maior volume, maior crescimento, maior queda).

## Tema claro fixo, sem modo escuro

A paleta foi validada (daltonismo e contraste) contra superfície clara. Modo escuro
exige uma segunda paleta com passos próprios validados contra a superfície escura - não é
inversão automática. Fora do escopo desta entrega por decisão, não por esquecimento.
Toda cor do projeto vive em `app/theme.py` (template Plotly global) e
`.streamlit/config.toml`; nenhum gráfico declara cor própria.

## O dashboard não calcula nada em pandas

As páginas só aplicam filtro (equivalente de WHERE) e agregação trivial (soma, contagem,
pivot). Janelas, quintis, percentuais acumulados e a definição de churn vivem nas views
versionadas em `sql/views/`. Se um número do dashboard divergir do SQL, o erro é do app,
não da análise - e a view continua auditável por quem nunca abriu o Python.

## Projeção usa a regressão mesmo com o baseline ganhando no teste

No split temporal (treino até dez/2025, teste jan-jun/2026) a média móvel de 3 meses
bateu a regressão por pouco: MAE 46,3k contra 51,9k, MAPE 18,9% contra 19,8%, R2 negativo
nos dois. Publiquei os números como são - a tabela da página de Previsão mostra o baseline
vencendo. A projeção de jul-dez/2026, porém, sai da regressão: média móvel realimentada
para frente converge para uma reta e nunca anteciparia o pico de novembro, que é o evento
mais importante do ano; a regressão carrega a dummy de novembro. Diferença de 12% no MAE,
medida em 6 observações, não justifica descartar o único modelo com estrutura sazonal.
Análise completa no notebook 03.

## Seed fixa no gerador

`random.Random(SEED)` com seed constante no código. Duas execuções geram o mesmo CSV
byte a byte, o que torna o dataset commitado reproduzível por qualquer avaliador e faz
da carga remota uma reprodução exata da local, não um retrabalho.

## Arquivos de view com prefixo numérico

`sql/views/` seguia a convenção de um arquivo por view com o nome da view, e o
`scripts/migrate.py` aplicava tudo em ordem alfabética. Só que `vw_vendas` é a base de que
onze das doze views leem, e `vw_vendas.sql` era o último nome do alfabeto: o primeiro arquivo
aplicado já fazia `FROM dw.vw_vendas`. Isso nunca falhou aqui porque o banco local ganhou as
views uma a uma ao longo dos blocos 2 a 4, e reaplicar `CREATE OR REPLACE` sobre view que já
existe funciona. Em banco zerado - o VPS, o `docker compose` com volume novo, o avaliador
clonando o repo - quebrava sempre.

Adotei o prefixo numérico que `sql/ddl/` já usava, agora refletindo a ordem de dependência
entre as views. O `sorted()` do migrate continua sendo a única regra de ordenação, sem código
novo. A alternativa era manter os nomes e listar a ordem dentro do `migrate.py`, mas aí uma
view nova que ficasse de fora da lista seria ignorada em silêncio, falha pior que a original,
que ao menos estourava. `tests/test_ordem_views.py` lê os arquivos na mesma ordem do migrate
e falha se alguma view referenciar outra ainda não criada.

## Título ancorado no container, faixa superior de 76px

Com `margin.t = 48`, o título (que por padrão se centra no meio da margem superior) e a legenda
horizontal (ancorada logo acima da área de plotagem) disputavam a mesma faixa de pixels e se
sobrepunham nos cinco gráficos com legenda. Passei o título para `yref="container"` com
`yanchor="top"`, o que o prende ao topo da figura independentemente da altura da margem, e abri a
faixa superior para 76px - o suficiente para título e legenda empilhados.

A margem maior vale para todo gráfico, inclusive os sem legenda. Aumentar só onde há legenda
economizaria espaço em branco, mas desalinharia as áreas de plotagem de gráficos lado a lado
(na Home, sazonalidade tem legenda e categorias não, e as duas dividem a mesma linha). Alinhamento
entre painéis vizinhos vale mais que 28px de altura.

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

## Modo escuro entrou, com claro como padrão (reverte "tema claro fixo")

Esta decisão substitui a anterior, que era "tema claro fixo, sem modo escuro". O motivo
original continua correto e não foi contornado: modo escuro exige uma segunda paleta com
passos próprios validados contra a superfície escura, e não é inversão automática da
clara. A diferença é que agora essa paleta existe e foi validada, então a condição que
segurava a decisão foi cumprida em vez de dispensada.

Os passos escuros são os que a paleta de referência documenta para superfície escura, dos
mesmos matizes. Medições contra `#1a1a19`, pelas mesmas checagens usadas no claro:

| Cenário | Separação sob daltonismo | Piso de visão normal | Contraste |
|---|---|---|---|
| Slots 1-4, pares adjacentes (barras, linhas) | ΔE 8,4 | ΔE 19,8 | todos acima de 3:1 |
| Slots 1-3, todos os pares (dispersão) | ΔE 9,4 | ΔE 20,9 | todos acima de 3:1 |

O alvo de daltonismo é 8 e o piso de visão normal é 15, então os dois cenários passam. O
escuro passa sem nenhum aviso: os avisos de contraste do projeto (aqua a 2,74:1 e amarelo
a 2,11:1) existem só no claro, e são cobertos pelo gêmeo tabular, que já é obrigatório
embaixo de todo gráfico.

Três escolhas que não saíram da tabela de referência e precisam de justificativa própria:

- **Cinza de de-emphasis escuro `#52514e`.** Dá 2,19:1 sobre o fundo escuro, o mesmo grau
  de recuo que `#c3c2b7` tem sobre o claro (1,75:1), e fica a ΔE 22,5-25,3 das três cores
  destacadas. O candidato mais claro `#6b6a64` seria mais visível (3,21:1) mas fica a 15,8
  do aqua, no limite do piso - o cinza começaria a competir com o destaque em vez de ficar
  atrás dele, que é o oposto do que a decisão de emphasis quer.
- **A rampa sequencial inverte no escuro.** Quem precisa recuar para o fundo é a ponta
  escura, não a clara. Isso também faz o passo 0 - usado como preenchimento da banda da
  previsão - continuar sendo o mais próximo da superfície nos dois modos sem a página
  saber de nada.
- **Status virou token por modo.** O delta do KPI é texto pequeno, onde a barra é 4,5:1 e
  não os 3:1 de marca, e nenhum hex único passa nos dois fundos. Bom: `#006300` no claro
  (7,35:1) e `#0ca30c` no escuro (5,19:1). Crítico: `#d03b3b` no claro (4,68:1) e
  `#e66767` no escuro (5,39:1). De quebra isso corrige uma falha que já existia: o claro
  usava `#0ca30c`, que dá 3,27:1 e reprova para texto.

Toda cor continua vivendo só em `app/theme.py`; nenhum gráfico declara cor própria. O que
mudou é que `theme.py` deixou de ser um módulo de constantes e passou a resolver a paleta
por sessão - ver a decisão seguinte.

O "claro como padrão" do título vale só para as duas decisões seguintes: a de "quem decide
o modo é o frontend" o revê, por um bug que ele não tinha como evitar. As duas paletas e a
validação continuam valendo integralmente.

## O tema é por sessão, então o template do Plotly deixou de ser global

`app/theme.py` registrava o template como efeito colateral de import e o marcava em
`pio.templates.default`. Módulo Python é cacheado por processo, então constante de módulo
é global do processo e não da sessão: com dois usuários em modos diferentes no mesmo
servidor, o primeiro a importar congelaria a paleta do segundo.

Agora `theme.paleta()` devolve a paleta da sessão corrente, os dois templates ficam
registrados sem nenhum ser o default, e `ui.grafico()` aplica o template por figura. É
uma chamada a mais por gráfico em troca de não ter estado de cor compartilhado entre
sessões. `tests/test_tema.py` falha se o default global voltar.

## Trocar de tema recarrega a página e zera os filtros

O Streamlit resolve o tema uma vez, no boot da página, e não expõe API Python para
trocá-lo em runtime: `st.context.theme` é somente leitura. O único gancho suportado é
`?embed_options=dark_theme` na URL, que vence tanto o `localStorage` quanto a preferência
do sistema operacional - e, ao contrário de `show_toolbar` e companhia, não depende de
`embed=true`, então nada do chrome da página é removido junto. Por isso o toggle é uma
âncora que navega de verdade, e não um `st.button`: widget só dispara rerun, e rerun não
recarrega.

A consequência é que a recarga reinicia a sessão e os filtros voltam ao padrão. Preferi
isso a serializar os seis filtros na query string, porque `app/filtros.py` já estava
pronto e correto e trocar de tema é ação de uma vez por visita. A sidebar avisa o
comportamento em vez de escondê-lo.

Um detalhe de implementação que decorre disso: `st.query_params` esconde `embed_options`,
então o Python não consegue ler o parâmetro que o frontend usa. Ele descobre o modo por
outro caminho - ver a decisão seguinte.

## Quem decide o modo é o frontend; o Python só pergunta qual saiu

Esta decisão corrige um bug e reverte a parte de "claro é o padrão, o tema do sistema
nunca é consultado" da decisão acima. O sintoma: num Chrome com
`prefers-color-scheme: dark`, o dashboard abria com o chrome do Streamlit escuro e os
gráficos claros, e o texto dos KPIs (`#0b0b0b`) ficava ilegível sobre `#1a1a19`. Persistia
mesmo com `?tema=claro` explícito na URL.

A causa está no bundle do `streamlit==1.60.0`, em duas funções:

- `createCustomThemes` monta **três** temas - Custom Theme Light, Custom Theme Dark e
  Custom Theme Auto - sempre que **qualquer uma** das subseções de tema tem conteúdo
  (`if (temLight || temDark)`). Basta o `[theme.dark]`. A seção antiga deste arquivo
  afirmava que era preciso declarar os dois lados, e essa premissa é que estava errada.
- `processThemeInput` resolve a preferência da URL (`embed_options`), depois a do
  `localStorage`; **se nenhuma das duas existe e há mais de um tema, ele escolhe o Auto**,
  que é `matchMedia('(prefers-color-scheme: dark)')`.

Então o frontend seguia o sistema operacional, e o `tema=claro|escuro` do projeto não
mudava nada: é parâmetro inventado aqui, e o frontend não o lê. Havia duas autoridades
decidindo o modo sem se falarem, e a divergência era estrutural, não um caso de borda.

Não existe configuração que force o claro mantendo o escuro disponível: tirar o
`[theme.dark]` derruba o Auto mas torna o escuro inalcançável, porque com tema custom o
Streamlit descarta os temas predefinidos. E `embed_options` não sobrevive à troca de
página - só é preservado sob `embed=true` -, então corrigir apenas o link do toggle
deixaria o bug voltar num F5 em página interna.

Ficou uma autoridade só. `theme.paleta()` não decide mais nada: devolve `ESCURO` quando
`st.context.theme.type` é `"dark"` e `CLARO` no resto, incluindo o `None` de quando não há
navegador do outro lado. O toggle passou a declarar `embed_options` nos dois sentidos, e o
parâmetro próprio saiu da URL junto com o espelho em `st.session_state`, que perdeu a
função. Chrome e gráfico não têm mais como divergir em nenhuma URL alcançável.

O preço é que o padrão deixou de ser claro e passou a ser o modo do sistema, o que
contraria o desenho original. Vale mais do que custa: quem escolhe pelo toggle continua
mandando, quem não escolhe recebe o modo que já pediu ao sistema operacional, e o estado
inconsistente deixou de existir. `st.context.theme` ser somente leitura é exatamente o que
se usa aqui - lê-se o modo, não se manda nele.

Uma limitação conhecida fica de pé: o valor chega junto do rerun do navegador, então uma
troca de tema do sistema no meio da sessão só alcança os gráficos na interação seguinte.

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

## Quinta página, reabrindo o teto de quatro telas do plano

O plano de produção fixou quatro telas nomeadas (Visão Geral, Clientes, Produtos, Previsão) e
nenhuma outra. Reabri essa decisão e aprovei uma quinta página, `Definições`. O motivo não é
querer mais tela: é que os números não se autoexplicam para quem abre o link público sem
contexto. O tile de churn não diz que a janela é de 90 dias, e os dez segmentos nomeados pelo
RFM aparecem nos gráficos sem que nada na tela diga que combinação de recência e frequência
define "Não pode perder" ou "Prestes a dormir". A definição existe, mas mora no README e nas
views - ou seja, exige sair do dashboard.

O teto de quatro telas era um artefato de planejamento, não um achado de usabilidade, e
planejamento se ajusta ao produto, não o contrário. O que não entrou foi a ideia de uma tela
de onboarding ensinando a usar os filtros: dashboard de quatro páginas com sidebar visível não
precisa de tutorial, e aba de glossário é, na prática, a página menos visitada de qualquer
dashboard. Por isso a quinta página é referência auditável (definição de cada KPI, a grade dos
dez segmentos RFM, limitações conhecidas), em tabela e não em prosa, e o peso da compreensão
fica na adjacência: tooltip em cada KPI e uma frase de leitura junto de cada gráfico. É o mesmo
princípio da descrição de medida do Power BI e do campo de legenda do Tableau - a definição
precisa estar ao lado do número, porque ninguém interrompe a leitura para ir procurá-la.

Se eu mudasse de ideia, o que sairia primeiro é a página, não os tooltips: eles carregam a
parte que de fato é lida.

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

## A marca da sidebar é um SVG gerado, não HTML

A marca são três linhas de mesma largura - `INSIGHTFLOW` em cima, `PROJETO` e `DESENVOLVE`
embaixo - no topo da barra lateral, acima do menu de páginas. Duas restrições do Streamlit
decidiram a implementação inteira.

A primeira é de posição. Tudo que passa por `st.sidebar` cai em `stSidebarUserContent`, que
fica **abaixo** do menu de páginas. O único ponto acima do menu é o cabeçalho da barra, e a
única API que escreve nele é `st.logo()`, que aceita imagem. Daí a marca ser imagem, e não
um `st.markdown` com HTML: não é preferência, é o que a posição pedida permite.

A segunda é de tipografia. Justificar três linhas à mesma medida exige controlar o espaço
entre letras, e o valor certo depende da fonte que o sistema operacional entrega - `PROJETO`
tem 7 caracteres contra os 10 de `DESENVOLVE`, então nenhum espaçamento fixo serve para as
duas. O SVG resolve isso de graça: `textLength` com `lengthAdjust="spacing"` estica cada
linha até a medida distribuindo a diferença nos avanços entre glifos, sem deformar as letras.
O retângulo fecha em qualquer máquina. Em HTML seria um `<span>` por letra.

Os números, todos em `app/ui.py`:

- **Bloco de 176 x 53px.** 176 é o maior bloco que cabe centralizado nos 240px úteis da barra
  deixando livres os 32px que o botão de recolher ocupa à direita. 53px de altura cabem nos
  60px do cabeçalho nativo, e é o alinhamento central dele que dá o respiro em cima e embaixo -
  se o bloco tivesse 64px, seria obrigatório reescrever a altura do cabeçalho e o offset do
  botão.
- **21px na primeira linha.** "INSIGHTFLOW" em negrito mede de 7,3 a 8,0 vezes o corpo conforme
  a fonte do sistema (Segoe UI no Windows, DejaVu Sans no Linux do contêiner). A 21px o pior
  caso dá 168px, ainda abaixo dos 176, então o ajuste é sempre espaçamento positivo. A 22px o
  pior caso ultrapassaria a medida e o `lengthAdjust` entraria em espaçamento negativo,
  encostando as letras.
- **A primeira linha também é esticada.** No espaçamento natural ela mediria entre 153px e
  168px conforme a fonte, e as duas de baixo, presas a uma medida fixa, só casariam com ela na
  máquina onde os números foram medidos.
- **Maiúscula nas duas linhas de baixo.** A justificação impõe 1,7em de espaçamento em
  `PROJETO` contra 0,9em em `DESENVOLVE`, e a diferença absoluta entre os dois é fixa em cerca
  de um dezoito avos da medida, independente do corpo: não há tamanho que a faça sumir. Em
  caixa alta isso lê como lockup editorial, o mesmo idioma de um kicker espaçado; em caixa de
  título leria como falha de renderização.
- **Azul na primeira linha, tinta secundária nas outras.** Nenhum token novo - a marca usa a
  paleta que já existe, resolvida por sessão como todo o resto. Contra o fundo da barra, o azul
  dá 4,19:1 no claro e 5,35:1 no escuro, e a 21px em negrito o critério aplicável é o de texto
  grande (3:1). A tinta secundária dá 7,53:1 e 10,88:1, acima dos 4,5:1 exigidos para os 12px
  do descritor. O cinza de rótulo de eixo foi descartado: 3,40:1 no claro, reprovado.
- **Uma variante de uma linha para a barra recolhida.** Ali o Streamlit mostra o mesmo logo no
  cabeçalho do app com teto de 32px, onde o descritor ficaria com 7px de corpo. Como a altura
  do viewBox e a altura renderizada coincidem, a escala é 1:1 e a palavra sai do mesmo tamanho
  da barra aberta: recolher tira o descritor e mais nada.

Dois custos aceitos, ambos sem contorno razoável:

- **O texto vira imagem.** O frontend do Streamlit escreve `alt="Logo"` fixo, e `<title>` ou
  `aria-label` dentro de um SVG carregado via `<img>` não chegam à tecnologia assistiva. A
  marca não é selecionável nem pesquisável. O que sobra: o nome do projeto já é anunciado pelo
  `<title>` do documento, que as cinco páginas definem em `st.set_page_config`. Corrigir o
  `alt` exigiria `unsafe_allow_javascript=True`, risco maior que o problema.
- **Três regras de CSS dependem de contrato privado.** `stSidebarLogo` e `stSidebarHeader` são
  `data-testid` internos, não API. Sem elas o Streamlit trava a imagem em 32px de altura. A
  degradação é segura: se os seletores mudarem, a marca volta a 32px alinhada à esquerda - feia,
  legível, sem estourar layout. Com `streamlit==1.60.0` pinado, a mudança só chega quando
  alguém subir a versão de propósito. `tests/test_marca.py` guarda a intenção das regras para
  que ninguém as apague achando que são decorativas.

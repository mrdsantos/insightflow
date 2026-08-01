# Storytelling analítico

A narrativa abaixo junta os achados dos notebooks e das views em uma história só, na
ordem em que um gestor precisaria ouvi-la. Cada seção aponta a página do dashboard onde
o número pode ser conferido ao vivo.

## 1. O negócio cresce, mas em degraus, não em rampa

Faturamento concretizado de R$ 6,07 milhões em 24 meses (jul/2024 a jun/2026). O segundo
ano roda num patamar visivelmente acima do primeiro: janeiro saltou de 186 mil (2025)
para 293 mil (2026), fevereiro de 180 mil para 331 mil. Só que o crescimento não veio
suave - veio em saltos de patamar, com meses atípicos para baixo no meio (abr/2026, 193
mil). Quem planeja estoque e caixa por "média dos últimos meses" erra dos dois lados.

*Onde ver: página Visão Geral, série mensal com sazonalidade ano a ano.*

## 2. Novembro não é um mês, é um evento

O pico de Black Friday domina a série: 335 mil em nov/2024 e 500 mil em nov/2025 - o
maior mês da história da base, 49% acima do novembro anterior e perto do dobro de um mês
típico. A sazonalidade é o padrão mais forte e mais confiável dos dados, e é também o
motivo de o modelo de previsão precisar de estrutura sazonal (seção 5).

*Onde ver: página Visão Geral; a comparação nov/2024 vs nov/2025 está na própria série.*

## 3. A receita é concentrada - e isso é risco operacional

Dois números contam a história da concentração:

- **Produtos**: 8 dos 30 SKUs respondem por 80% do faturamento. O líder, Notebook Gamer,
  sozinho carrega 22,6%. A cauda de ~22 produtos existe, mas não paga as contas.
- **Clientes**: o top 10% dos clientes concentra 41,4% da receita.

Concentração assim corta dos dois lados: esforço comercial focado rende muito, mas a
perda de poucos clientes grandes (ou o desabastecimento de um único SKU líder em
novembro) machuca desproporcionalmente.

*Onde ver: página Produtos (Pareto em escala única) e página Clientes (share do top 10%).*

## 4. Há dinheiro esfriando na base de clientes

O RFM sobre os 580 clientes com venda concretizada nomeia 10 segmentos. Três importam
para ação imediata:

- **135 Campeões** - compram com frequência, gastam mais, compraram há pouco. São o
  grupo a proteger: qualquer atrito com eles custa caro (seção 3).
- **105 Em Risco** - já foram bons clientes e estão há tempo demais sem comprar. É o
  segmento com melhor retorno esperado de campanha de reativação: valor comprovado,
  relacionamento ainda morno.
- **39 Perdidos** - alta recência, baixo tudo. Reativação aqui é cara e improvável;
  melhor entender o motivo da perda do que insistir.

O corte operacional de churn é 90 dias sem comprar (percentil 90 do intervalo real entre
recompras é 101 dias - o número saiu dos dados, não de convenção).

*Onde ver: página Clientes (heatmap RFM, dispersão com os 3 segmentos destacados,
retenção por coorte).*

## 5. A previsão: útil como ordem de grandeza, honesta sobre o limite

Para jul/2026 o modelo projeta ~R$ 321 mil, com banda de 207 a 435 mil. No teste
temporal (treinar até dez/2025, prever jan-jun/2026), o baseline de média móvel bateu a
regressão por pouco - 2026 abriu acima do que 2025 sugeria e o modelo reativo se adaptou
mais rápido - e ambos tiveram R2 negativo. O resultado está publicado como é, não
maquiado: com 24 observações mensais, nenhum modelo prevê bem mês a mês.

A projeção usa a regressão mesmo assim porque é o único dos dois modelos que carrega
sazonalidade: média móvel projetada para frente vira uma reta e nunca anteciparia
novembro - justamente o mês que mais importa (seção 2). Uso recomendado: planejamento de
faixa (pessimista/base/otimista via banda), nunca meta mensal.

*Onde ver: página Previsão (projeção tracejada com banda, tabela modelo vs baseline).*

## O que eu faria a seguir

1. Campanha de reativação nos 105 Em Risco antes de novembro - é o maior estoque de
   receita dormindo, e o evento do ano é o gancho natural.
2. Plano de contingência de estoque para os 8 SKUs que pagam 80% das contas, com
   prioridade absoluta no Notebook Gamer em outubro/novembro.
3. Reavaliar o modelo quando houver um terceiro novembro na base: é o ponto em que a
   sazonalidade estimada deixa de ser média de dois eventos.

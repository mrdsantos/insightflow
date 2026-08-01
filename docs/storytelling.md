# Storytelling analitico

A narrativa abaixo junta os achados dos notebooks e das views em uma historia so, na
ordem em que um gestor precisaria ouvi-la. Cada secao aponta a pagina do dashboard onde
o numero pode ser conferido ao vivo.

## 1. O negocio cresce, mas em degraus, nao em rampa

Faturamento concretizado de R$ 6,07 milhoes em 24 meses (jul/2024 a jun/2026). O segundo
ano roda num patamar visivelmente acima do primeiro: janeiro saltou de 186 mil (2025)
para 293 mil (2026), fevereiro de 180 mil para 331 mil. So que o crescimento nao veio
suave - veio em saltos de patamar, com meses atipicos para baixo no meio (abr/2026, 193
mil). Quem planeja estoque e caixa por "media dos ultimos meses" erra dos dois lados.

*Onde ver: pagina Visao Geral, serie mensal com sazonalidade ano a ano.*

## 2. Novembro nao e um mes, e um evento

O pico de Black Friday domina a serie: 335 mil em nov/2024 e 500 mil em nov/2025 - o
maior mes da historia da base, 49% acima do novembro anterior e perto do dobro de um mes
tipico. A sazonalidade e o padrao mais forte e mais confiavel dos dados, e e tambem o
motivo de o modelo de previsao precisar de estrutura sazonal (secao 5).

*Onde ver: pagina Visao Geral; a comparacao nov/2024 vs nov/2025 esta na propria serie.*

## 3. A receita e concentrada - e isso e risco operacional

Dois numeros contam a historia da concentracao:

- **Produtos**: 8 dos 30 SKUs respondem por 80% do faturamento. O lider, Notebook Gamer,
  sozinho carrega 22,6%. A cauda de ~22 produtos existe, mas nao paga as contas.
- **Clientes**: o top 10% dos clientes concentra 41,4% da receita.

Concentracao assim corta dos dois lados: esforco comercial focado rende muito, mas a
perda de poucos clientes grandes (ou o desabastecimento de um unico SKU lider em
novembro) machuca desproporcionalmente.

*Onde ver: pagina Produtos (Pareto em escala unica) e pagina Clientes (share do top 10%).*

## 4. Ha dinheiro esfriando na base de clientes

O RFM sobre os 580 clientes com venda concretizada nomeia 10 segmentos. Tres importam
para acao imediata:

- **135 Campeoes** - compram com frequencia, gastam mais, compraram ha pouco. Sao o
  grupo a proteger: qualquer atrito com eles custa caro (secao 3).
- **105 Em Risco** - ja foram bons clientes e estao ha tempo demais sem comprar. E o
  segmento com melhor retorno esperado de campanha de reativacao: valor comprovado,
  relacionamento ainda morno.
- **39 Perdidos** - alta recencia, baixo tudo. Reativacao aqui e cara e improvavel;
  melhor entender o motivo da perda do que insistir.

O corte operacional de churn e 90 dias sem comprar (percentil 90 do intervalo real entre
recompras e 101 dias - o numero saiu dos dados, nao de convencao).

*Onde ver: pagina Clientes (heatmap RFM, dispersao com os 3 segmentos destacados,
retencao por coorte).*

## 5. A previsao: util como ordem de grandeza, honesta sobre o limite

Para jul/2026 o modelo projeta ~R$ 321 mil, com banda de 207 a 435 mil. No teste
temporal (treinar ate dez/2025, prever jan-jun/2026), o baseline de media movel bateu a
regressao por pouco - 2026 abriu acima do que 2025 sugeria e o modelo reativo se adaptou
mais rapido - e ambos tiveram R2 negativo. O resultado esta publicado como e, nao
maquiado: com 24 observacoes mensais, nenhum modelo preve bem mes a mes.

A projecao usa a regressao mesmo assim porque e o unico dos dois modelos que carrega
sazonalidade: media movel projetada para frente vira uma reta e nunca anteciparia
novembro - justamente o mes que mais importa (secao 2). Uso recomendado: planejamento de
faixa (pessimista/base/otimista via banda), nunca meta mensal.

*Onde ver: pagina Previsao (projecao tracejada com banda, tabela modelo vs baseline).*

## O que eu faria a seguir

1. Campanha de reativacao nos 105 Em Risco antes de novembro - e o maior estoque de
   receita dormindo, e o evento do ano e o gancho natural.
2. Plano de contingencia de estoque para os 8 SKUs que pagam 80% das contas, com
   prioridade absoluta no Notebook Gamer em outubro/novembro.
3. Reavaliar o modelo quando houver um terceiro novembro na base: e o ponto em que a
   sazonalidade estimada deixa de ser media de dois eventos.

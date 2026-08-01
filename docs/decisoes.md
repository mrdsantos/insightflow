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

## Seed fixa no gerador

`random.Random(SEED)` com seed constante no codigo. Duas execucoes geram o mesmo CSV
byte a byte, o que torna o dataset commitado reproduzivel por qualquer avaliador e faz
da carga remota uma reproducao exata da local, nao um retrabalho.

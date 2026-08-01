# Relatório de qualidade dos dados

Gerado pelo pipeline a cada execução - não editar na mão. Sem timestamp de propósito: execução idêntica gera arquivo idêntico.

## Visão geral

| Métrica | Valor |
|---|---|
| Linhas no CSV / staging | 8209 |
| Linhas válidas carregadas no fato | 7643 |
| Linhas rejeitadas (quarentena) | 445 (5,4%) |
| Duplicatas de id_transacao descartadas | 121 |
| Clientes / produtos / localidades distintos | 603 / 30 / 15 |

## Antes da limpeza

### Nulos por coluna (staging)

| Coluna | Nulos |
|---|---|
| id_transacao | 55 |
| data_venda | 58 |
| id_cliente | 51 |
| nome_produto | 48 |
| valor_unitario | 42 |

### Formatos de data em circulação

| Formato | Linhas |
|---|---|
| iso (aaaa-mm-dd) | 4817 |
| dd/mm/aaaa | 2070 |
| dd-mm-aaaa | 1221 |
| nulo | 58 |
| invalido | 43 |

### Formas de moeda em circulação

| Forma | Linhas |
|---|---|
| R$ 1.234,56 | 3227 |
| 1234.56 | 2956 |
| 1.234,56 | 1955 |
| nulo | 42 |
| invalido | 29 |

### Inconsistências de texto

- Categorias distintas antes da normalização: 20
- Status distintos antes da normalização: 18

## Depois da limpeza

- Categorias distintas no dw: 6
- Status distintos no dw: 5
- Nulos em campo chave no fato: 0 (barrados na validação)
- Datas e valores: tipados (DATE / NUMERIC), um formato só

## Quarentena por motivo

| Motivo | Linhas |
|---|---|
| quantidade nao positiva | 83 |
| campo chave nulo: data_venda | 58 |
| campo chave nulo: id_transacao | 55 |
| campo chave nulo: id_cliente | 51 |
| campo chave nulo: nome_produto | 48 |
| data invalida | 42 |
| campo chave nulo: valor_unitario | 42 |
| status invalido | 40 |
| valor invalido | 26 |

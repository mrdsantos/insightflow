# Relatorio de qualidade dos dados

Gerado pelo pipeline em 2026-07-31 21:32. Regenerado a cada execucao - nao editar na mao.

## Visao geral

| Metrica | Valor |
|---|---|
| Linhas no CSV / staging | 8209 |
| Linhas validas carregadas no fato | 7643 |
| Linhas rejeitadas (quarentena) | 445 (5.4%) |
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

### Formatos de data em circulacao

| Formato | Linhas |
|---|---|
| iso (aaaa-mm-dd) | 4817 |
| dd/mm/aaaa | 2070 |
| dd-mm-aaaa | 1221 |
| nulo | 58 |
| invalido | 43 |

### Formas de moeda em circulacao

| Forma | Linhas |
|---|---|
| R$ 1.234,56 | 3227 |
| 1234.56 | 2956 |
| 1.234,56 | 1955 |
| nulo | 42 |
| invalido | 29 |

### Inconsistencias de texto

- Categorias distintas antes da normalizacao: 20
- Status distintos antes da normalizacao: 18

## Depois da limpeza

- Categorias distintas no dw: 6
- Status distintos no dw: 5
- Nulos em campo chave no fato: 0 (barrados na validacao)
- Datas e valores: tipados (DATE / NUMERIC), um formato so

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

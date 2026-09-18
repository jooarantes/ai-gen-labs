# Processo: nps_ecommerce

## Esquema esperado
| coluna | tipo | obrigatoria | observacao |
| --- | --- | --- | --- |
| id_avaliacao | texto | sim | chave da avaliacao |
| data_avaliacao | data ISO (YYYY-MM-DD) | sim | data da resposta |
| id_cliente | texto | sim | identificador do cliente |
| nota_nps | inteiro 0-10 | sim | nota da pesquisa NPS |
| canal | texto | sim | app, site ou marketplace |
| dispositivo | texto | nao | valores padronizados, com "Nao informado" quando ausente |
| categoria_compra | texto | sim | categoria do pedido |
| valor_pedido | decimal | sim | valor numerico em reais |
| uf | texto | sim | sigla do estado |
| primeiro_pedido | texto | sim | Sim ou Nao |
| mes_referencia | texto | sim | derivado de data_avaliacao e do nome do arquivo |
| arquivo_origem | texto | sim | nome do CSV bruto de entrada |

## Origem e frequencia
Arquivos mensais em `dados_brutos/` com o padrao `nps_ecommerce_YYYY-MM.csv`.
O processo foi desenhado para rodar sempre que um novo mes chegar, consolidando o historico sem sobrescrever os brutos.

## Etapas
1. `limpeza.py` - padroniza colunas, remove duplicatas exatas, converte tipos e valida a base.
2. `etl.py` - le todos os arquivos mensais, aplica a limpeza e grava a base historica consolidada.
3. `gerar_dashboard.py` - resume o historico, calcula NPS por mes e por segmento e gera o dashboard HTML.

## Como executar
```powershell
python processos/nps_ecommerce/etl.py --input-dir dados_brutos --output-csv dados_tratados/nps_ecommerce_tratado.csv
python processos/nps_ecommerce/gerar_dashboard.py --input-csv dados_tratados/nps_ecommerce_tratado.csv --output-html dashboards/dashboard_nps_ecommerce.html
```

## Decisoes registradas
- Duplicatas exatas sao removidas automaticamente. No lote inicial, abril teve 3 linhas removidas e maio teve 4.
- `dispositivo` recebe `Nao informado` quando vem vazio.
- `primeiro_pedido` e normalizado para `Sim` e `Nao`.
- `valor_pedido` e convertido para numero decimal para permitir analise historica e calculos de ticket medio.
- `mes_referencia` e derivado do nome do arquivo e validado contra `data_avaliacao` para evitar mistura de meses.

## Historico de execucoes
| data | arquivo de entrada | resultado |
| --- | --- | --- |
| 2026-06-10 | `dados_brutos/nps_ecommerce_2026-04.csv`, `dados_brutos/nps_ecommerce_2026-05.csv` | consolidacao gerada com 1.595 linhas; dashboard `dashboards/dashboard_nps_ecommerce.html` atualizado |
| 2026-06-10 | `dados_brutos/nps_ecommerce_2026-04.csv`, `dados_brutos/nps_ecommerce_2026-05.csv`, `dados_brutos/nps_ecommerce_2026-06.csv` | consolidacao atualizada com 2.414 linhas; dashboard `dashboards/dashboard_nps_ecommerce.html` atualizado com junho |

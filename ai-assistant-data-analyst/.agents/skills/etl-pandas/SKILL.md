---
name: etl-pandas
description: Use esta skill sempre que o usuário precisar criar scripts de ETL, pipelines de dados, automação de carga ou consolidação de arquivos com Python/pandas. Acione quando mencionar "ETL", "pipeline", "automatizar a carga", "consolidar planilhas", "juntar arquivos", "transformar dados", "rotina de dados", "processar todo mês", ou quando a tarefa envolver extrair dados de uma ou mais fontes, transformá-los e salvar em formato pronto para análise — mesmo que a palavra ETL não apareça.
---

# Scripts de ETL com pandas

Skill genérica para gerar pipelines ETL reutilizáveis em Python/pandas, aplicáveis a qualquer fonte tabular (CSV, Excel, JSON, múltiplos arquivos, APIs simples).

## Princípios

- **Reexecutável e idempotente.** O script deve poder rodar quantas vezes for preciso sobre os mesmos dados sem duplicar ou corromper resultados.
- **Genérico via parâmetros, não via edição.** Caminhos, períodos e filtros entram por argumentos de linha de comando ou arquivo de config — nunca exigem editar o código.
- **Falhar ruidosamente.** Dados de entrada fora do esperado devem parar o pipeline com mensagem clara, não produzir saída silenciosamente errada.
- **Separação extract / transform / load.** Cada etapa é uma função testável de forma independente.

## Antes de escrever o script

Entenda e confirme com o usuário: quais as fontes (arquivos, pastas, padrão de nomes), com que frequência o processo roda, qual o formato de saída desejado e quais validações importam (colunas obrigatórias, totais que devem bater, períodos sem buracos). Se já existir script de limpeza do dataset (skill `limpeza-dados`), reutilize-o como parte do transform em vez de reescrever a lógica.

## Estrutura padrão do script

Gere `etl_<nome_processo>.py`:

```python
"""ETL: <descrição em uma linha>. Gerado em <data>.
Uso: python etl_<nome>.py --entrada pasta/ --saida dados_tratados/base.csv
"""
import argparse
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# --- CONFIG (esquema esperado, regras fixas do negócio) ---
COLUNAS_OBRIGATORIAS = [...]

def extract(origem: Path) -> pd.DataFrame:
    """Lê a(s) fonte(s). Suporta múltiplos arquivos com glob quando fizer sentido."""

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza + transformações de negócio, uma sub-função por regra."""

def validate(df: pd.DataFrame) -> None:
    """Falha com mensagem clara se o resultado violar as regras."""

def load(df: pd.DataFrame, destino: Path) -> None:
    """Salva a saída. Nunca sobrescreve dados brutos."""

def main():
    ...

if __name__ == "__main__":
    main()
```

Pontos de atenção ao implementar:

- **extract**: detecte separador/encoding com fallback; ao consolidar múltiplos arquivos, registre no log quantos foram lidos e adicione coluna de origem (`_arquivo_origem`) quando útil para auditoria.
- **transform**: cada regra de negócio em sub-função nomeada com comentário do porquê; tipos convertidos explicitamente; datas sempre para datetime.
- **validate**: colunas obrigatórias presentes, sem nulos em chaves, totais/contagens dentro do esperado. Use `assert` com mensagens ou raise ValueError.
- **load**: crie as pastas de destino se não existirem; prefira CSV UTF-8 ou parquet para bases grandes; logue o caminho final e o nº de linhas.

## Convenção de pastas

```
projeto/
├── dados_brutos/      # fontes originais, intocadas
├── dados_tratados/    # saídas do ETL
└── processos/<nome>/  # scripts e config do processo (ver skill processo-dados)
```

## Entrega

- O script ETL
- Uma execução de demonstração com os dados disponíveis, mostrando o log
- Instrução de uso em 2-3 linhas (comando exato para rodar de novo)

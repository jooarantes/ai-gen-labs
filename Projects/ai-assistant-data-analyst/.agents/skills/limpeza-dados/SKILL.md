---
name: limpeza-dados
description: Use esta skill sempre que o usuário quiser limpar, tratar ou avaliar a qualidade de um conjunto de dados tabular (CSV, Excel, etc.). Acione quando mencionar "limpar dados", "tratar dados", "dados sujos", "valores nulos", "duplicatas", "padronizar colunas", "qualidade dos dados", ou quando apresentar um dataset com problemas evidentes de formatação, tipos ou consistência — mesmo que não peça limpeza explicitamente. Use antes de qualquer análise ou dashboard se os dados ainda não foram tratados.
---

# Limpeza de Dados

Skill genérica para diagnosticar e tratar qualquer dataset tabular, gerando um script de limpeza reutilizável em Python/pandas.

## Princípios

- **Diagnosticar antes de tratar.** Nunca aplique tratamentos sem antes perfilar os dados e entender os problemas reais.
- **Decisões de negócio são do usuário.** Remover linhas, imputar valores e tratar outliers mudam o resultado das análises. Em casos ambíguos, apresente as opções com impacto estimado (ex.: "remover duplicatas elimina 230 linhas, 4% da base") e pergunte.
- **Tudo vira script reutilizável.** O produto final não é só o arquivo limpo — é um script parametrizado que repete a limpeza em novas versões dos mesmos dados.
- **Nunca sobrescrever dados brutos.** O original permanece intacto; o resultado vai para arquivo novo.

## Fluxo de trabalho

### 1. Perfil dos dados

Execute o script bundled de perfil:

```bash
python scripts/perfil_dados.py <caminho_do_arquivo> [--sep ";"] [--encoding latin-1]
```

Ele imprime um relatório com: dimensões, tipos por coluna, % de nulos, duplicatas, cardinalidade, valores de exemplo, outliers (IQR) e possíveis problemas de encoding/formato. Se o script não cobrir o formato do arquivo, perfile manualmente com pandas.

### 2. Diagnóstico para o usuário

Resuma os problemas encontrados em linguagem de negócio, com impacto quantificado. Classifique cada problema:

- **Correção segura** (aplicar direto): espaços extras, padronização de nomes de colunas, conversão de tipos óbvia (ex.: "R$ 1.234,56" → float), datas em formato misto.
- **Decisão necessária** (perguntar): remoção de duplicatas, imputação ou remoção de nulos, tratamento de outliers, linhas inválidas.

### 3. Script de limpeza

Gere `limpeza_<nome_dataset>.py` com esta estrutura:

```python
"""Limpeza do dataset <nome>. Gerado em <data>.
Uso: python limpeza_<nome>.py entrada.csv saida.csv
"""
import argparse
import pandas as pd

def carregar(caminho): ...
def limpar(df):
    # uma função por tratamento, com comentário explicando o porquê
    ...
def validar(df):
    # checagens pós-limpeza: sem nulos nas colunas críticas, tipos corretos, etc.
    ...

if __name__ == "__main__":
    ...
```

Regras do script: caminhos via argumentos (nada hardcoded), uma função por tratamento com comentário do motivo da decisão, validação ao final que falha ruidosamente se o resultado não atender às regras, e log do que foi alterado (linhas removidas, valores imputados).

### 4. Entrega

- Arquivo limpo (mesmo formato do original, sufixo `_limpo`)
- Script de limpeza
- Resumo curto: o que foi tratado, quantas linhas/valores afetados, o que ficou pendente de decisão

## Convenção de pastas

Quando trabalhando dentro de um projeto com processo padronizado (ver skill `processo-dados`), salve o script em `processos/<dataset>/` e os dados em `dados_tratados/`. Fora disso, salve junto ao arquivo original.

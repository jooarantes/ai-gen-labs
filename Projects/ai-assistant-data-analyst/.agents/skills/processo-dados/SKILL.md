---
name: processo-dados
description: Use esta skill SEMPRE que o usuário apresentar um conjunto de dados (CSV, Excel, planilha, base) para análise — é o ponto de entrada antes das skills de limpeza, ETL e dashboard. Acione quando o usuário enviar/mencionar um arquivo de dados novo, disser "analisa esses dados", "chegou a base de X", "monta um processo para esses dados", "padroniza essa análise", "todo mês recebo esse arquivo", ou quando um dataset já conhecido reaparecer. Decide entre análise pontual ou processo padronizado reutilizável e gerencia os processos salvos em processos/.
---

# Processo de Dados (orquestrador)

Ponto de entrada do assistente de análise. Quando um dataset chega, esta skill decide o caminho: rodar um processo padronizado já existente, criar um novo processo padronizado, ou fazer uma análise pontual. As skills `limpeza-dados`, `etl-pandas` e `dashboard-html` são as ferramentas; esta skill é o fluxo.

## Fluxo ao receber um dataset

### 1. Verificar se o dataset já é conhecido

Liste `processos/` na pasta do projeto. Cada subpasta tem um `processo.md` com o esquema esperado (colunas, tipos). Compare as colunas do arquivo recebido com os esquemas registrados.

- **Match encontrado**: informe o usuário ("reconheci este dataset como o processo X") e ofereça: executar o processo padrão, ou fazer algo pontual desta vez. Se o arquivo tiver colunas a mais/a menos que o esquema, avise antes de rodar.
- **Sem match**: é um dataset novo → passo 2.

### 2. Dataset novo: perfilar e perguntar

Faça um perfil rápido (use `scripts/perfil_dados.py` da skill `limpeza-dados`) e apresente um resumo do que os dados contêm. Então pergunte ao usuário (via AskUserQuestion):

- **Análise pontual** — resolver a necessidade de agora, sem persistir processo.
- **Processo padronizado** — além de resolver agora, registrar o processo para reuso (ideal para dados recorrentes: relatório mensal, extração semanal, etc.).

Se o usuário mencionar recorrência ("todo mês", "sempre que chegar"), recomende o processo padronizado.

### 3a. Caminho pontual

Use as skills necessárias (`limpeza-dados` → análise → `dashboard-html` se pedir visual) e entregue os resultados. Nada é registrado em `processos/` — mas, ao final, se a análise pareceu repetível, ofereça transformá-la em processo padronizado.

### 3b. Caminho padronizado

Crie `processos/<nome-do-dataset>/` com:

```
processos/<nome>/
├── processo.md        # documentação do processo (ver template abaixo)
├── limpeza.py         # gerado via skill limpeza-dados
├── etl.py             # gerado via skill etl-pandas (se houver transformação/consolidação)
└── gerar_dashboard.py # agrega dados e regenera o dashboard (se houver dashboard)
```

Template do `processo.md`:

```markdown
# Processo: <nome>

## Esquema esperado
| coluna | tipo | obrigatória | observação |

## Origem e frequência
<de onde vem o arquivo, com que frequência chega>

## Etapas
1. limpeza.py — <o que trata>
2. etl.py — <o que transforma>
3. gerar_dashboard.py — <KPIs e gráficos produzidos>

## Como executar
<comandos exatos, em ordem>

## Decisões registradas
<ex.: duplicatas removidas por chave X; nulos em Y imputados com mediana — decidido em dd/mm/aaaa>

## Histórico de execuções
| data | arquivo de entrada | resultado |
```

O `processo.md` é a memória do processo: registre nele toda decisão de tratamento tomada com o usuário, para que execuções futuras sejam consistentes sem precisar perguntar de novo.

### 4. Execuções recorrentes

Ao rodar um processo existente: execute os scripts na ordem documentada, valide o resultado, atualize o histórico de execuções no `processo.md` e entregue os outputs (dados tratados e/ou dashboard atualizado). Se algo no arquivo novo violar o esquema, pare e pergunte antes de improvisar — pode ser mudança real na fonte que exige atualizar o processo.

**Delegação a subagente**: se houver a ferramenta de subagentes disponível, delegue a execução recorrente a um subagente seguindo as instruções de `agentes/executor-processo-dados.md` na pasta do projeto (passe o conteúdo do arquivo como prompt, mais os caminhos do processo e do arquivo de entrada). Isso mantém a conversa principal limpa — só o relatório final volta. Criação e alteração de processos nunca são delegadas: exigem diálogo com o usuário.

## Convenção de pastas do projeto

```
projeto/
├── dados_brutos/     # arquivos originais recebidos, nunca modificados
├── dados_tratados/   # saídas de limpeza/ETL
├── dashboards/       # HTMLs gerados
└── processos/        # um subdiretório por processo padronizado
```

Crie essas pastas conforme forem necessárias, não todas de uma vez.

## Princípios

- Esta skill nunca refaz o trabalho das outras: limpeza, ETL e dashboard seguem suas skills específicas; aqui só se decide o caminho e se mantém o registro.
- Processos padronizados existem para dar consistência: o mesmo arquivo de entrada deve sempre produzir o mesmo tipo de saída, com as mesmas regras.
- Pergunte antes de criar processo para dados claramente de uso único — padronizar tudo gera ruído.

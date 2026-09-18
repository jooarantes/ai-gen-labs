---
name: dashboard-html
description: Use esta skill sempre que o usuário quiser criar dashboards, painéis, visualizações de dados ou relatórios visuais para liderança/gestão. Acione quando mencionar "dashboard", "painel", "gráficos", "KPIs", "visualizar os dados", "apresentar os números", "relatório visual", "mostrar para o diretor/liderança", ou quando uma análise de dados pedir entrega visual — mesmo que o usuário não diga a palavra dashboard. Gera um arquivo HTML único e interativo que abre em qualquer navegador.
---

# Dashboard HTML para Liderança

Skill genérica para transformar qualquer dataset tabular em um dashboard interativo de arquivo único (HTML + Chart.js), pronto para enviar por e-mail ou abrir em qualquer navegador, sem instalação.

## Princípios

- **O dashboard responde perguntas, não exibe dados.** Antes de montar, identifique as 3-5 perguntas que a liderança quer responder (tendência? comparação? meta?). Cada gráfico existe para responder uma delas.
- **Títulos com conclusão.** Em vez de "Vendas por mês", escreva "Vendas crescem 12% no trimestre, puxadas pelo Sudeste". O executivo lê o título; o gráfico é a evidência.
- **Menos é mais.** KPIs no topo, 3-6 gráficos no máximo. Se sobrar conteúdo, vai para uma seção "Detalhes" colapsada no fim.
- **Arquivo único e offline-friendly.** Dados embutidos como JSON no próprio HTML; única dependência externa é o CDN do Chart.js.

## Antes de montar

Se os dados ainda estiverem sujos, trate primeiro (skill `limpeza-dados`). Depois confirme com o usuário, se não estiver claro: público (diretoria? gerência?), as perguntas a responder, e se há metas/valores de referência para comparar.

## Estrutura do arquivo

Gere `dashboard_<nome>.html` com esta anatomia:

1. **Cabeçalho**: título do dashboard, período coberto, data de atualização.
2. **Faixa de KPIs**: 3-5 cartões com o número grande, rótulo curto e variação vs. período anterior ou meta (▲/▼ com cor).
3. **Gráficos**: grid responsivo (CSS grid, 2 colunas em desktop, 1 em mobile). Tipos: linha para tendência, barra para comparação, barra horizontal para rankings, rosca apenas para composição com ≤5 fatias. Evite pizza com muitas fatias e eixos duplos.
4. **Filtros simples** (quando os dados pedem): `<select>` por período/categoria que refaz os gráficos via JS puro.
5. **Rodapé**: fonte dos dados e nota metodológica em uma linha.

## Padrões técnicos

- Chart.js via `https://cdn.jsdelivr.net/npm/chart.js` (única dependência).
- Dados em `const DADOS = [...]` — JSON pré-agregado no Python, não a base linha a linha (mantém o arquivo leve; agregue antes com pandas).
- Formato brasileiro: `Intl.NumberFormat('pt-BR')` para números, `R$` para moeda, datas `dd/mm/aaaa`, abreviações `mil`/`mi` para números grandes nos KPIs.
- Paleta sóbria e consistente: uma cor primária para a métrica principal, cinzas para contexto, vermelho/verde apenas para variações negativas/positivas. Fundo claro, sem gradientes chamativos.
- Sem `localStorage` e sem bibliotecas além do Chart.js.

## Checklist antes de entregar

- Abre direto do disco (file://) sem erro no console?
- KPIs batem com os dados de origem? (confira os números com pandas antes de embutir)
- Títulos contam a conclusão, não só o eixo?
- Legível em tela de notebook e em celular?
- Período e data de atualização visíveis?

## Entrega

O arquivo HTML salvo na pasta do projeto + 2-3 linhas destacando os principais insights que o dashboard mostra. Quando o dataset tiver processo padronizado (skill `processo-dados`), salve também o script Python que regenera o JSON agregado, para o dashboard ser atualizável.

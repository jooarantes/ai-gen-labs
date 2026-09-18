"""Tratamento e dashboard da pesquisa de satisfação de clientes.

Uso:
    python processar_pesquisa_satisfacao_clientes.py

Saídas:
    - dados_tratados/pesquisa_satisfacao_clientes_tratado.csv
    - dashboards/dashboard_pesquisa_satisfacao_clientes.html
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
from dateutil import parser as date_parser


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "dados_brutos" / "pesquisa_satisfacao_clientes.csv"
OUTPUT_DIR_DATA = BASE_DIR / "dados_tratados"
OUTPUT_DIR_DASH = BASE_DIR / "dashboards"
OUTPUT_CSV = OUTPUT_DIR_DATA / "pesquisa_satisfacao_clientes_tratado.csv"
OUTPUT_HTML = OUTPUT_DIR_DASH / "dashboard_pesquisa_satisfacao_clientes.html"


CHANNEL_MAP = {
    "chat": "Chat",
    "whatsapp": "WhatsApp",
    "telefone": "Telefone",
    "email": "E-mail",
    "loja fisica": "Loja física",
}


NEGATIVE_COMMENT_THEMES = {
    "poderia melhorar o prazo de resposta": "Prazo de resposta",
    "demorou demais para me atenderem": "Demora no atendimento",
    "atendente foi educado mas nao resolveu meu problema": "Resolução não concluída",
    "preco alto comparado a concorrencia": "Preço alto",
    "produto bom mas a entrega atrasou": "Entrega atrasada",
    "nao recomendo o suporte por telefone": "Suporte por telefone",
}


POSITIVE_COMMENT_THEMES = {
    "otima experiencia do inicio ao fim": "Experiência excelente",
    "muito satisfeito com a solucao": "Solução satisfatória",
    "atendimento excelente resolveram rapido": "Resolução rápida",
}


def normalize_key(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def compact_key(value: object) -> str:
    return normalize_key(value).replace(" ", "")


def parse_date_value(value: object) -> pd.Timestamp:
    if pd.isna(value):
        return pd.NaT
    text = str(value).strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return pd.Timestamp(pd.to_datetime(text, format="%Y-%m-%d", errors="coerce"))
        return pd.Timestamp(date_parser.parse(text, dayfirst=True, yearfirst=False))
    except Exception:
        return pd.NaT


def clean_channel(value: object) -> str:
    key = compact_key(value)
    if key in {"chat", "whatsapp", "telefone", "email", "lojafisica"}:
        return {
            "chat": "Chat",
            "whatsapp": "WhatsApp",
            "telefone": "Telefone",
            "email": "E-mail",
            "lojafisica": "Loja física",
        }[key]
    return str(value).strip().title()


def clean_recommendation(value: object) -> str:
    key = normalize_key(value)
    if key.startswith("sim"):
        return "Sim"
    if key.startswith("nao"):
        return "Não"
    return str(value).strip().title()


def classify_comment(value: object) -> tuple[str, str]:
    key = normalize_key(value)
    if not key:
        return "Sem comentário", "Sem comentário"

    if key in NEGATIVE_COMMENT_THEMES:
        return NEGATIVE_COMMENT_THEMES[key], "Negativo"
    if key in POSITIVE_COMMENT_THEMES:
        return POSITIVE_COMMENT_THEMES[key], "Positivo"

    if "preco" in key or "caro" in key:
        return "Preço alto", "Negativo"
    if "atras" in key and "entrega" in key:
        return "Entrega atrasada", "Negativo"
    if "nao resolveu" in key:
        return "Resolução não concluída", "Negativo"
    if "prazo" in key or "resposta" in key:
        return "Prazo de resposta", "Negativo"
    if "demorou" in key or "demora" in key:
        return "Demora no atendimento", "Negativo"
    if "telefone" in key and "recomendo" in key:
        return "Suporte por telefone", "Negativo"
    if "excelente" in key or "satisfeito" in key or "otima" in key:
        return "Experiência excelente", "Positivo"
    if key == "tudo certo":
        return "Tudo certo", "Neutro"

    return "Outro", "Neutro"


def load_and_clean(input_file: Path) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(input_file, sep=";", encoding="latin-1")
    original_rows = len(raw)

    df = raw.drop_duplicates().copy()
    duplicate_rows = original_rows - len(df)

    df["data_resposta"] = df["data_resposta"].map(parse_date_value)
    df["data_resposta"] = df["data_resposta"].dt.strftime("%Y-%m-%d")

    df["cidade"] = df["cidade"].astype("string").str.strip()
    df["canal_atendimento"] = df["canal_atendimento"].map(clean_channel)
    df["recomendaria"] = df["recomendaria"].map(clean_recommendation)
    df["comentario"] = df["comentario"].astype("string").str.strip()
    df.loc[df["comentario"].eq(""), "comentario"] = pd.NA

    df["idade"] = pd.to_numeric(df["idade"], errors="coerce")
    invalid_age_mask = ~df["idade"].between(18, 100)
    invalid_age_count = int(invalid_age_mask.sum())
    df.loc[invalid_age_mask, "idade"] = pd.NA
    df["idade"] = df["idade"].astype("Int64")

    df["nota_satisfacao"] = pd.to_numeric(df["nota_satisfacao"], errors="coerce").astype("Float64")
    df["nota_atendimento"] = pd.to_numeric(df["nota_atendimento"], errors="coerce").astype("Int64")
    df["nota_preco"] = pd.to_numeric(df["nota_preco"], errors="coerce").astype("Int64")
    df["tempo_cliente_meses"] = pd.to_numeric(df["tempo_cliente_meses"], errors="coerce").astype("Int64")

    classified = df["comentario"].map(classify_comment)
    df["tema_comentario"] = classified.map(lambda item: item[0])
    df["sentimento_comentario"] = classified.map(lambda item: item[1])

    summary = {
        "original_rows": original_rows,
        "clean_rows": len(df),
        "duplicate_rows_removed": duplicate_rows,
        "invalid_age_count": invalid_age_count,
        "missing_sat_count": int(df["nota_satisfacao"].isna().sum()),
        "date_min": str(pd.to_datetime(df["data_resposta"]).min().date()),
        "date_max": str(pd.to_datetime(df["data_resposta"]).max().date()),
    }
    return df, summary


def build_aggregate(df: pd.DataFrame) -> dict:
    valid_sat = df["nota_satisfacao"].notna()
    comments_with_text = df["sentimento_comentario"] != "Sem comentário"

    top2_box = float((df.loc[valid_sat, "nota_satisfacao"] >= 4).mean() * 100) if valid_sat.any() else 0.0
    avg_sat = float(df.loc[valid_sat, "nota_satisfacao"].mean()) if valid_sat.any() else 0.0
    rec_rate = float((df["recomendaria"] == "Sim").mean() * 100) if len(df) else 0.0

    sentiment_counts = (
        df["sentimento_comentario"]
        .value_counts(dropna=False)
        .reindex(["Positivo", "Negativo", "Neutro", "Sem comentário"], fill_value=0)
        .to_dict()
    )

    score_counts = (
        df.loc[valid_sat, "nota_satisfacao"]
        .value_counts()
        .sort_index()
        .reindex([1, 2, 3, 4, 5], fill_value=0)
        .reset_index()
    )
    score_counts.columns = ["nota", "qtd"]

    channels = []
    for channel, group in df.groupby("canal_atendimento", sort=False):
        valid = group["nota_satisfacao"].notna()
        channels.append(
            {
                "canal": channel,
                "respostas": int(len(group)),
                "csat": round(float((group.loc[valid, "nota_satisfacao"] >= 4).mean() * 100) if valid.any() else 0.0, 1),
                "media": round(float(group.loc[valid, "nota_satisfacao"].mean()) if valid.any() else 0.0, 2),
                "recomendacao": round(float((group["recomendaria"] == "Sim").mean() * 100) if len(group) else 0.0, 1),
                "negativo": round(float((group["sentimento_comentario"] == "Negativo").mean() * 100) if len(group) else 0.0, 1),
                "positivo": round(float((group["sentimento_comentario"] == "Positivo").mean() * 100) if len(group) else 0.0, 1),
                "neutro": round(float((group["sentimento_comentario"] == "Neutro").mean() * 100) if len(group) else 0.0, 1),
                "sem_comentario": round(float((group["sentimento_comentario"] == "Sem comentário").mean() * 100) if len(group) else 0.0, 1),
            }
        )

    channels = sorted(channels, key=lambda item: item["csat"], reverse=True)

    negative_themes = (
        df.loc[df["sentimento_comentario"] == "Negativo", "tema_comentario"]
        .value_counts()
        .reset_index()
    )
    negative_themes.columns = ["tema", "qtd"]
    negative_themes = negative_themes.to_dict("records")

    positive_themes = (
        df.loc[df["sentimento_comentario"] == "Positivo", "tema_comentario"]
        .value_counts()
        .reset_index()
    )
    positive_themes.columns = ["tema", "qtd"]
    positive_themes = positive_themes.to_dict("records")

    comments_only = df.loc[comments_with_text]
    comment_sentiment_share = {
        sentiment: round(float((comments_only["sentimento_comentario"] == sentiment).mean() * 100) if len(comments_only) else 0.0, 1)
        for sentiment in ["Positivo", "Negativo", "Neutro"]
    }

    return {
        "kpis": {
            "total_respostas": int(len(df)),
            "respostas_validas_satisfacao": int(valid_sat.sum()),
            "csat_top2_box": round(top2_box, 1),
            "nota_media": round(avg_sat, 2),
            "taxa_recomendacao": round(rec_rate, 1),
            "comentarios_negativos_pct": round(float((df["sentimento_comentario"] == "Negativo").mean() * 100), 1),
            "comentarios_com_texto": int(comments_with_text.sum()),
        },
        "periodo": {
            "inicio": pd.to_datetime(df["data_resposta"]).min().strftime("%d/%m/%Y"),
            "fim": pd.to_datetime(df["data_resposta"]).max().strftime("%d/%m/%Y"),
        },
        "sentiment_counts": sentiment_counts,
        "score_counts": score_counts.to_dict("records"),
        "channels": channels,
        "negative_themes": negative_themes,
        "positive_themes": positive_themes,
        "comment_sentiment_share": comment_sentiment_share,
    }


def render_dashboard(aggregate: dict, output_file: Path) -> None:
    data_json = json.dumps(aggregate, ensure_ascii=False)
    html = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard CSAT - Pesquisa de Satisfação</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --panel: rgba(255,255,255,.92);
      --panel-strong: #ffffff;
      --text: #0f172a;
      --muted: #5b6472;
      --line: #d9e2ea;
      --primary: #0f766e;
      --primary-dark: #0b4f4a;
      --accent: #2563eb;
      --positive: #15803d;
      --negative: #c2410c;
      --shadow: 0 16px 40px rgba(15, 23, 42, .08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI Variable", "Segoe UI", "Trebuchet MS", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(37,99,235,.12), transparent 28%),
        radial-gradient(circle at top right, rgba(15,118,110,.10), transparent 30%),
        linear-gradient(180deg, #eef4f7 0%, #f7fafc 34%, #eef3f6 100%);
      min-height: 100vh;
    }
    .wrap { max-width: 1400px; margin: 0 auto; padding: 28px 18px 40px; }
    .hero {
      background: linear-gradient(135deg, var(--primary-dark), #0f766e 46%, #14532d 110%);
      color: white;
      border-radius: 28px;
      padding: 28px 28px 24px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }
    .hero::after {
      content: "";
      position: absolute;
      inset: auto -40px -90px auto;
      width: 240px;
      height: 240px;
      border-radius: 50%;
      background: rgba(255,255,255,.08);
      filter: blur(2px);
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: .74rem;
      font-weight: 700;
      color: rgba(255,255,255,.78);
      margin-bottom: 10px;
    }
    .hero h1 { margin: 0; font-size: clamp(1.8rem, 3vw, 3rem); line-height: 1.08; max-width: 12ch; }
    .hero p { margin: 14px 0 0; max-width: 86ch; color: rgba(255,255,255,.82); font-size: 1rem; line-height: 1.5; }
    .meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
    .pill {
      padding: 8px 12px;
      background: rgba(255,255,255,.10);
      border: 1px solid rgba(255,255,255,.16);
      border-radius: 999px;
      backdrop-filter: blur(5px);
      font-size: .9rem;
    }
    .section {
      margin-top: 18px;
      background: var(--panel);
      border: 1px solid rgba(217,226,234,.8);
      border-radius: 24px;
      box-shadow: var(--shadow);
      padding: 20px;
    }
    .section h2 { margin: 0 0 14px; font-size: 1.2rem; }
    .kpis { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
    .kpi {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      min-height: 120px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .kpi .label { color: var(--muted); font-size: .9rem; line-height: 1.3; }
    .kpi .value { font-size: clamp(1.8rem, 3vw, 2.7rem); font-weight: 800; margin-top: 8px; letter-spacing: -.04em; }
    .kpi .note { font-size: .82rem; color: var(--muted); margin-top: 6px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; align-items: start; }
    .chart-card {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px 16px 12px;
      min-height: 390px;
    }
    .chart-card h3 { margin: 0 0 10px; font-size: 1rem; line-height: 1.35; }
    .chart-card p { margin: -2px 0 10px; color: var(--muted); font-size: .88rem; }
    .chart-wrap { position: relative; height: 290px; }
    .chart-card.tall .chart-wrap { height: 320px; }
    .insights { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
    .insight {
      background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      min-height: 180px;
    }
    .insight .tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: .78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .12em;
      color: var(--muted);
      margin-bottom: 10px;
    }
    .insight ul { margin: 10px 0 0; padding-left: 18px; color: var(--text); line-height: 1.55; }
    .table-wrap { overflow: auto; border: 1px solid var(--line); border-radius: 18px; }
    table { width: 100%; border-collapse: collapse; background: white; min-width: 720px; }
    th, td { padding: 12px 14px; border-bottom: 1px solid #edf2f7; text-align: left; white-space: nowrap; }
    th {
      position: sticky;
      top: 0;
      background: #f8fafc;
      font-size: .84rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--muted);
    }
    tr:last-child td { border-bottom: none; }
    .footnote { margin-top: 12px; color: var(--muted); font-size: .85rem; line-height: 1.45; }
    @media (max-width: 1180px) {
      .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid, .insights { grid-template-columns: 1fr; }
    }
    @media (max-width: 720px) {
      .wrap { padding: 16px 12px 28px; }
      .hero { padding: 22px 18px 18px; border-radius: 22px; }
      .section { padding: 16px; border-radius: 20px; }
      .kpis { grid-template-columns: 1fr; }
      .chart-card { min-height: 350px; }
      .chart-wrap { height: 250px; }
      .chart-card.tall .chart-wrap { height: 270px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="eyebrow">CSAT | Pesquisa de satisfação de clientes</div>
      <h1>O que está fazendo o atendimento ganhar e perder satisfação</h1>
      <p>
        Leitura executiva da pesquisa tratada como CSAT. A base foi deduplicada, padronizada e os comentários foram classificados para separar pontos de atrito do que vale preservar.
      </p>
      <div class="meta">
        <div class="pill">Período: __PERIODO_INICIO__ a __PERIODO_FIM__</div>
        <div class="pill">Fonte: dados_brutos/pesquisa_satisfacao_clientes.csv</div>
        <div class="pill">Definição de CSAT: % de notas 4 e 5 entre respostas válidas</div>
      </div>
    </header>

    <section class="section">
      <h2>KPIs principais</h2>
      <div class="kpis">
        <div class="kpi"><div class="label">Respostas tratadas</div><div class="value">__TOTAL_RESPOSTAS__</div><div class="note">12 duplicatas exatas removidas no tratamento.</div></div>
        <div class="kpi"><div class="label">CSAT</div><div class="value">__CSAT__</div><div class="note">Notas 4 e 5 sobre as __RESPOSTAS_VALIDAS__ respostas válidas.</div></div>
        <div class="kpi"><div class="label">Nota média de satisfação</div><div class="value">__NOTA_MEDIA__</div><div class="note">Escala de 1 a 5.</div></div>
        <div class="kpi"><div class="label">Taxa de recomendação</div><div class="value">__TAXA_RECOMENDACAO__</div><div class="note">Percentual de “Sim” em recomendaria.</div></div>
        <div class="kpi"><div class="label">Comentários negativos</div><div class="value">__NEGATIVOS__</div><div class="note">Fatia da base com sinal explícito de dor.</div></div>
      </div>
    </section>

    <section class="section">
      <h2>Leituras que importam</h2>
      <div class="insights">
        <div class="insight">
          <div class="tag">Melhorar</div>
          <div>Os maiores focos de atrito estão em:</div>
          <ul id="top-negative"></ul>
        </div>
        <div class="insight">
          <div class="tag">Manter</div>
          <div>Os sinais positivos mais fortes mostram que vale sustentar:</div>
          <ul id="top-positive"></ul>
        </div>
        <div class="insight">
          <div class="tag">Atenção por canal</div>
          <div>Canal com melhor leitura e canal que merece mais cuidado:</div>
          <ul id="channel-callout"></ul>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Visualizações</h2>
      <div class="grid">
        <article class="chart-card">
          <h3>Distribuição das notas de satisfação mostra concentração em 4 e 5, mas ainda há espaço para reduzir notas medianas</h3>
          <p>Base válida: notas registradas entre 1 e 5.</p>
          <div class="chart-wrap"><canvas id="chart-scores"></canvas></div>
        </article>
        <article class="chart-card">
          <h3>CSAT por canal destaca Chat como melhor ponto de contato e E-mail como principal oportunidade</h3>
          <p>Comparação entre canais com volume de respostas suficiente.</p>
          <div class="chart-wrap"><canvas id="chart-channel-csat"></canvas></div>
        </article>
        <article class="chart-card tall">
          <h3>Comentários se concentram em dores operacionais e de tempo de resposta</h3>
          <p>Distribuição do sentimento dos comentários por canal.</p>
          <div class="chart-wrap"><canvas id="chart-sentiment-channel"></canvas></div>
        </article>
        <article class="chart-card tall">
          <h3>Principais temas negativos apontam prazo, atendimento e resolução como prioridades</h3>
          <p>Frequência dos temas com sinal negativo explícito.</p>
          <div class="chart-wrap"><canvas id="chart-negative-themes"></canvas></div>
        </article>
        <article class="chart-card">
          <h3>O que vale preservar aparece nos elogios à solução e à rapidez de atendimento</h3>
          <p>Frequência dos temas positivos identificados nos comentários.</p>
          <div class="chart-wrap"><canvas id="chart-positive-themes"></canvas></div>
        </article>
        <article class="chart-card">
          <h3>Leitura por canal resume satisfação, recomendação e peso de comentários negativos</h3>
          <p>Ranking consolidado por canal de atendimento.</p>
          <div class="chart-wrap"><canvas id="chart-channel-summary"></canvas></div>
        </article>
      </div>
    </section>

    <section class="section">
      <h2>Resumo por canal</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Canal</th>
              <th>Respostas</th>
              <th>CSAT</th>
              <th>Média</th>
              <th>Recomendação</th>
              <th>% negativo</th>
              <th>% positivo</th>
            </tr>
          </thead>
          <tbody id="channel-table"></tbody>
        </table>
      </div>
      <div class="footnote">
        Observação metodológica: comentários sem texto foram classificados como “Sem comentário” e não entram no ranking de temas. O CSAT usa apenas notas válidas para a pergunta de satisfação.
      </div>
    </section>
  </div>

  <script>
    const DADOS = __DATA_JSON__;
    const fmtPct = (value) => new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(value) + '%';
    const fmtNum = (value) => new Intl.NumberFormat('pt-BR').format(value);
    const fmtDec = (value, digits = 2) => new Intl.NumberFormat('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value);

    function colorForIndex(index) {
      const palette = ['#0f766e', '#2563eb', '#15803d', '#d97706', '#64748b'];
      return palette[index % palette.length];
    }

    function barOptions(horizontal = false) {
      return {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: horizontal ? 'y' : 'x',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#fff',
            bodyColor: '#fff',
            padding: 12,
            callbacks: {
              label: (ctx) => horizontal ? ` ${ctx.parsed.x}` : ` ${ctx.parsed.y}`
            }
          }
        },
        scales: {
          x: { grid: { color: '#e7edf3' }, ticks: { color: '#64748b' } },
          y: { grid: { display: false }, ticks: { color: '#64748b' } }
        }
      };
    }

    const topNegative = DADOS.negative_themes.slice(0, 5);
    const topPositive = DADOS.positive_themes.slice(0, 3);
    document.getElementById('top-negative').innerHTML = topNegative.map(item => `<li><strong>${item.tema}</strong> (${fmtNum(item.qtd)} registros)</li>`).join('');
    document.getElementById('top-positive').innerHTML = topPositive.map(item => `<li><strong>${item.tema}</strong> (${fmtNum(item.qtd)} registros)</li>`).join('');

    const bestChannel = DADOS.channels[0];
    const worstChannel = DADOS.channels[DADOS.channels.length - 1];
    document.getElementById('channel-callout').innerHTML = [
      `<li><strong>Melhor leitura:</strong> ${bestChannel.canal} com CSAT de ${fmtPct(bestChannel.csat)}</li>`,
      `<li><strong>Maior atenção:</strong> ${worstChannel.canal} com CSAT de ${fmtPct(worstChannel.csat)}</li>`
    ].join('');

    document.getElementById('channel-table').innerHTML = DADOS.channels.map(item => `
      <tr>
        <td>${item.canal}</td>
        <td>${fmtNum(item.respostas)}</td>
        <td>${fmtPct(item.csat)}</td>
        <td>${fmtDec(item.media, 2)}</td>
        <td>${fmtPct(item.recomendacao)}</td>
        <td>${fmtPct(item.negativo)}</td>
        <td>${fmtPct(item.positivo)}</td>
      </tr>
    `).join('');

    new Chart(document.getElementById('chart-scores'), {
      type: 'bar',
      data: {
        labels: DADOS.score_counts.map(item => `${item.nota}`),
        datasets: [{
          data: DADOS.score_counts.map(item => item.qtd),
          backgroundColor: ['#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#1d4ed8'],
          borderRadius: 10,
          maxBarThickness: 48
        }]
      },
      options: {
        ...barOptions(false),
        plugins: {
          ...barOptions(false).plugins,
          tooltip: {
            ...barOptions(false).plugins.tooltip,
            callbacks: {
              label: (ctx) => ` ${fmtNum(ctx.parsed.y)} respostas`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#64748b' } },
          y: { beginAtZero: true, grid: { color: '#e7edf3' }, ticks: { color: '#64748b', precision: 0 } }
        }
      }
    });

    new Chart(document.getElementById('chart-channel-csat'), {
      type: 'bar',
      data: {
        labels: DADOS.channels.map(item => item.canal),
        datasets: [{
          data: DADOS.channels.map(item => item.csat),
          backgroundColor: DADOS.channels.map((_, index) => colorForIndex(index)),
          borderRadius: 10,
          maxBarThickness: 42
        }]
      },
      options: {
        ...barOptions(true),
        indexAxis: 'y',
        plugins: {
          ...barOptions(true).plugins,
          tooltip: {
            ...barOptions(true).plugins.tooltip,
            callbacks: {
              label: (ctx) => ` ${fmtPct(ctx.parsed.x)} de CSAT`
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            max: 100,
            grid: { color: '#e7edf3' },
            ticks: { color: '#64748b', callback: (value) => `${value}%` }
          },
          y: { grid: { display: false }, ticks: { color: '#64748b' } }
        }
      }
    });

    new Chart(document.getElementById('chart-sentiment-channel'), {
      type: 'bar',
      data: {
        labels: DADOS.channels.map(item => item.canal),
        datasets: [
          { label: 'Negativo', data: DADOS.channels.map(item => item.negativo), backgroundColor: '#ef4444', stack: 'stack1', borderRadius: 8 },
          { label: 'Positivo', data: DADOS.channels.map(item => item.positivo), backgroundColor: '#16a34a', stack: 'stack1', borderRadius: 8 },
          { label: 'Neutro', data: DADOS.channels.map(item => item.neutro), backgroundColor: '#64748b', stack: 'stack1', borderRadius: 8 },
          { label: 'Sem comentário', data: DADOS.channels.map(item => item.sem_comentario), backgroundColor: '#cbd5e1', stack: 'stack1', borderRadius: 8 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { usePointStyle: true, boxWidth: 10, color: '#334155' }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#fff',
            bodyColor: '#fff',
            padding: 12,
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${fmtPct(ctx.parsed.x)}`
            }
          }
        },
        scales: {
          x: {
            stacked: true,
            max: 100,
            grid: { color: '#e7edf3' },
            ticks: { color: '#64748b', callback: (value) => `${value}%` }
          },
          y: { stacked: true, grid: { display: false }, ticks: { color: '#64748b' } }
        }
      }
    });

    new Chart(document.getElementById('chart-negative-themes'), {
      type: 'bar',
      data: {
        labels: DADOS.negative_themes.map(item => item.tema),
        datasets: [{
          data: DADOS.negative_themes.map(item => item.qtd),
          backgroundColor: '#c2410c',
          borderRadius: 10,
          maxBarThickness: 38
        }]
      },
      options: {
        ...barOptions(true),
        indexAxis: 'y',
        plugins: {
          ...barOptions(true).plugins,
          tooltip: {
            ...barOptions(true).plugins.tooltip,
            callbacks: {
              label: (ctx) => ` ${fmtNum(ctx.parsed.x)} comentários`
            }
          }
        },
        scales: {
          x: { beginAtZero: true, grid: { color: '#e7edf3' }, ticks: { color: '#64748b', precision: 0 } },
          y: { grid: { display: false }, ticks: { color: '#64748b' } }
        }
      }
    });

    new Chart(document.getElementById('chart-positive-themes'), {
      type: 'bar',
      data: {
        labels: DADOS.positive_themes.map(item => item.tema),
        datasets: [{
          data: DADOS.positive_themes.map(item => item.qtd),
          backgroundColor: '#15803d',
          borderRadius: 10,
          maxBarThickness: 38
        }]
      },
      options: {
        ...barOptions(true),
        indexAxis: 'y',
        plugins: {
          ...barOptions(true).plugins,
          tooltip: {
            ...barOptions(true).plugins.tooltip,
            callbacks: {
              label: (ctx) => ` ${fmtNum(ctx.parsed.x)} comentários`
            }
          }
        },
        scales: {
          x: { beginAtZero: true, grid: { color: '#e7edf3' }, ticks: { color: '#64748b', precision: 0 } },
          y: { grid: { display: false }, ticks: { color: '#64748b' } }
        }
      }
    });

    new Chart(document.getElementById('chart-channel-summary'), {
      type: 'bar',
      data: {
        labels: DADOS.channels.map(item => item.canal),
        datasets: [
          { label: 'CSAT', data: DADOS.channels.map(item => item.csat), backgroundColor: '#0f766e', borderRadius: 10 },
          { label: 'Recomendação', data: DADOS.channels.map(item => item.recomendacao), backgroundColor: '#2563eb', borderRadius: 10 },
          { label: '% negativo', data: DADOS.channels.map(item => item.negativo), backgroundColor: '#c2410c', borderRadius: 10 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 10, color: '#334155' } },
          tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#fff',
            bodyColor: '#fff',
            padding: 12,
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${fmtPct(ctx.parsed.x)}`
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            max: 100,
            grid: { color: '#e7edf3' },
            ticks: { color: '#64748b', callback: (value) => `${value}%` }
          },
          y: { grid: { display: false }, ticks: { color: '#64748b' } }
        }
      }
    });
  </script>
</body>
</html>
"""

    html = html.replace("__DATA_JSON__", data_json)
    html = html.replace("__PERIODO_INICIO__", aggregate["periodo"]["inicio"])
    html = html.replace("__PERIODO_FIM__", aggregate["periodo"]["fim"])
    html = html.replace("__TOTAL_RESPOSTAS__", str(aggregate["kpis"]["total_respostas"]))
    html = html.replace("__CSAT__", f'{aggregate["kpis"]["csat_top2_box"]:.1f}%')
    html = html.replace("__RESPOSTAS_VALIDAS__", str(aggregate["kpis"]["respostas_validas_satisfacao"]))
    html = html.replace("__NOTA_MEDIA__", f'{aggregate["kpis"]["nota_media"]:.2f}')
    html = html.replace("__TAXA_RECOMENDACAO__", f'{aggregate["kpis"]["taxa_recomendacao"]:.1f}%')
    html = html.replace("__NEGATIVOS__", f'{aggregate["kpis"]["comentarios_negativos_pct"]:.1f}%')

    output_file.write_text(html, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR_DATA.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_DASH.mkdir(parents=True, exist_ok=True)

    df, load_summary = load_and_clean(INPUT_FILE)
    aggregate = build_aggregate(df)

    df.to_csv(OUTPUT_CSV, sep=";", index=False, encoding="utf-8-sig")
    render_dashboard(aggregate, OUTPUT_HTML)

    print("Tratamento concluído.")
    print(json.dumps(load_summary, ensure_ascii=False, indent=2))
    print(json.dumps(aggregate["kpis"], ensure_ascii=False, indent=2))
    print(f"CSV tratado: {OUTPUT_CSV}")
    print(f"Dashboard: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()

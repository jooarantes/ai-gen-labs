"""Gera o dashboard historico de NPS do e-commerce.

Uso:
    python processos/nps_ecommerce/gerar_dashboard.py --input-csv dados_tratados/nps_ecommerce_tratado.csv --output-html dashboards/dashboard_nps_ecommerce.html
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


MESES_PT = {
    "01": "jan",
    "02": "fev",
    "03": "mar",
    "04": "abr",
    "05": "mai",
    "06": "jun",
    "07": "jul",
    "08": "ago",
    "09": "set",
    "10": "out",
    "11": "nov",
    "12": "dez",
}


def formatar_mes(mes_referencia: str) -> str:
    ano, mes = mes_referencia.split("-")
    return f"{MESES_PT[mes]}/{ano}"


def calcular_nps(df: pd.DataFrame) -> dict:
    total = len(df)
    if total == 0:
        return {
            "respostas": 0,
            "promoters_pct": 0.0,
            "passives_pct": 0.0,
            "detractors_pct": 0.0,
            "nps": 0.0,
            "avg_score": 0.0,
            "avg_ticket": 0.0,
        }

    promoters = (df["nota_nps"] >= 9).mean() * 100
    passives = df["nota_nps"].between(7, 8).mean() * 100
    detractors = (df["nota_nps"] <= 6).mean() * 100

    return {
        "respostas": int(total),
        "promoters_pct": round(float(promoters), 1),
        "passives_pct": round(float(passives), 1),
        "detractors_pct": round(float(detractors), 1),
        "nps": round(float(promoters - detractors), 1),
        "avg_score": round(float(df["nota_nps"].mean()), 2),
        "avg_ticket": round(float(df["valor_pedido"].mean()), 2),
    }


def agregar_segmento(df: pd.DataFrame, coluna: str) -> list[dict]:
    itens = []
    for valor, grupo in df.groupby(coluna, dropna=False):
        item = calcular_nps(grupo)
        item[coluna] = "Nao informado" if pd.isna(valor) else str(valor)
        itens.append(item)
    itens = sorted(itens, key=lambda x: x["nps"], reverse=True)
    return itens


def montar_dados(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["data_avaliacao"] = pd.to_datetime(df["data_avaliacao"], errors="raise")
    df["mes_referencia"] = df["mes_referencia"].astype(str)

    meses = sorted(df["mes_referencia"].unique().tolist())
    mensal = []
    for mes in meses:
        grupo = df.loc[df["mes_referencia"] == mes]
        resumo = calcular_nps(grupo)
        resumo["mes_referencia"] = mes
        resumo["mes_label"] = formatar_mes(mes)
        mensal.append(resumo)

    mensal_df = pd.DataFrame(mensal)
    current_month = mensal_df.iloc[-1].to_dict()
    previous_month = mensal_df.iloc[-2].to_dict() if len(mensal_df) > 1 else None

    current_df = df.loc[df["mes_referencia"] == current_month["mes_referencia"]].copy()

    segments = {
        "canal": agregar_segmento(current_df, "canal"),
        "dispositivo": agregar_segmento(current_df, "dispositivo"),
        "categoria_compra": agregar_segmento(current_df, "categoria_compra"),
        "uf": agregar_segmento(current_df, "uf"),
        "primeiro_pedido": agregar_segmento(current_df, "primeiro_pedido"),
    }

    monthly_share = []
    for mes in meses:
        grupo = df.loc[df["mes_referencia"] == mes]
        total = len(grupo)
        monthly_share.append(
            {
                "mes_referencia": mes,
                "mes_label": formatar_mes(mes),
                "promoters_pct": round(float((grupo["nota_nps"] >= 9).mean() * 100), 1) if total else 0.0,
                "passives_pct": round(float(grupo["nota_nps"].between(7, 8).mean() * 100), 1) if total else 0.0,
                "detractors_pct": round(float((grupo["nota_nps"] <= 6).mean() * 100), 1) if total else 0.0,
            }
        )

    best_channel = segments["canal"][0] if segments["canal"] else None
    worst_channel = segments["canal"][-1] if segments["canal"] else None
    best_category = segments["categoria_compra"][0] if segments["categoria_compra"] else None
    worst_category = segments["categoria_compra"][-1] if segments["categoria_compra"] else None

    delta_nps = None
    delta_respostas = None
    delta_avg_ticket = None
    if previous_month is not None:
        delta_nps = round(float(current_month["nps"] - previous_month["nps"]), 1)
        delta_respostas = int(current_month["respostas"] - previous_month["respostas"])
        delta_avg_ticket = round(float(current_month["avg_ticket"] - previous_month["avg_ticket"]), 2)

    return {
        "metadata": {
            "source_files": sorted(df["arquivo_origem"].dropna().astype(str).unique().tolist()),
            "period_start": str(df["data_avaliacao"].min().date()),
            "period_end": str(df["data_avaliacao"].max().date()),
            "generated_at": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
        },
        "monthly": mensal_df.to_dict("records"),
        "monthly_share": monthly_share,
        "current_month": current_month,
        "previous_month": previous_month,
        "segments": segments,
        "insights": {
            "best_channel": best_channel,
            "worst_channel": worst_channel,
            "best_category": best_category,
            "worst_category": worst_category,
            "delta_nps": delta_nps,
            "delta_respostas": delta_respostas,
            "delta_avg_ticket": delta_avg_ticket,
        },
    }


def render_html(dados: dict) -> str:
    payload = json.dumps(dados, ensure_ascii=False)

    def fmt_num_py(value: float | int, digits: int = 0) -> str:
        if digits == 0:
            return f"{int(round(float(value))):,}".replace(",", ".")
        text = f"{float(value):,.{digits}f}"
        return text.replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_pct_py(value: float | int) -> str:
        return f"{fmt_num_py(value, 1)}%"

    def fmt_money_py(value: float | int) -> str:
        return f"R$ {fmt_num_py(value, 2)}"

    def fmt_signed_py(value: float | int | None, digits: int = 1) -> str:
        if value is None:
            return "N/A"
        sign = "+" if float(value) > 0 else ""
        return f"{sign}{fmt_num_py(value, digits)}"

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard NPS Ecommerce</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg: #f4f7fb;
      --card: rgba(255,255,255,.95);
      --text: #102033;
      --muted: #607084;
      --line: #d8e2ec;
      --primary: #0f766e;
      --primary-dark: #0b4f4a;
      --accent: #2563eb;
      --good: #15803d;
      --warn: #b45309;
      --bad: #c2410c;
      --shadow: 0 18px 45px rgba(16,32,51,.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Trebuchet MS", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(15,118,110,.16), transparent 24%),
        radial-gradient(circle at top right, rgba(37,99,235,.12), transparent 28%),
        linear-gradient(180deg, #eef3f8 0%, var(--bg) 100%);
      min-height: 100vh;
    }}
    .wrap {{ max-width: 1500px; margin: 0 auto; padding: 26px 18px 38px; }}
    .hero {{
      background: linear-gradient(135deg, var(--primary-dark), var(--primary) 55%, #134e4a 110%);
      color: white;
      border-radius: 28px;
      padding: 28px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      right: -80px;
      bottom: -120px;
      width: 280px;
      height: 280px;
      border-radius: 50%;
      background: rgba(255,255,255,.08);
    }}
    .eyebrow {{
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: .72rem;
      font-weight: 700;
      opacity: .8;
    }}
    .hero h1 {{
      margin: 10px 0 0;
      font-size: clamp(1.9rem, 3vw, 3rem);
      line-height: 1.04;
      max-width: 14ch;
    }}
    .hero p {{
      margin: 14px 0 0;
      max-width: 92ch;
      color: rgba(255,255,255,.84);
      line-height: 1.55;
    }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
    .pill {{
      border: 1px solid rgba(255,255,255,.18);
      background: rgba(255,255,255,.11);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: .9rem;
      backdrop-filter: blur(6px);
    }}
    .section {{
      margin-top: 18px;
      background: var(--card);
      border: 1px solid rgba(216,226,236,.8);
      border-radius: 24px;
      box-shadow: var(--shadow);
      padding: 20px;
    }}
    .section h2 {{ margin: 0 0 14px; font-size: 1.2rem; }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
    }}
    .kpi {{
      background: white;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      min-height: 124px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .kpi .label {{ color: var(--muted); font-size: .88rem; line-height: 1.25; }}
    .kpi .value {{ font-size: clamp(1.75rem, 2.8vw, 2.55rem); font-weight: 800; letter-spacing: -.04em; margin-top: 8px; }}
    .kpi .note {{ color: var(--muted); font-size: .82rem; margin-top: 6px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      align-items: start;
    }}
    .chart-card {{
      background: white;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px 16px 12px;
      min-height: 380px;
    }}
    .chart-card h3 {{ margin: 0; font-size: 1rem; line-height: 1.35; }}
    .chart-card p {{ margin: 8px 0 10px; color: var(--muted); font-size: .88rem; }}
    .chart-wrap {{ position: relative; height: 286px; }}
    .chart-card.tall .chart-wrap {{ height: 320px; }}
    .insights {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }}
    .insight {{
      background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      min-height: 160px;
    }}
    .insight .tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--muted);
      font-size: .78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .12em;
      margin-bottom: 10px;
    }}
    .insight ul {{ margin: 10px 0 0; padding-left: 18px; line-height: 1.55; }}
    .table-wrap {{ overflow: auto; border: 1px solid var(--line); border-radius: 18px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; min-width: 760px; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #edf2f7; text-align: left; white-space: nowrap; }}
    th {{
      position: sticky;
      top: 0;
      background: #f8fafc;
      color: var(--muted);
      font-size: .82rem;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    tr:last-child td {{ border-bottom: none; }}
    .footnote {{ margin-top: 12px; color: var(--muted); font-size: .85rem; line-height: 1.45; }}
    @media (max-width: 1180px) {{
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid, .insights {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 720px) {{
      .wrap {{ padding: 16px 12px 28px; }}
      .hero {{ padding: 22px 18px 18px; border-radius: 22px; }}
      .section {{ padding: 16px; border-radius: 20px; }}
      .kpis {{ grid-template-columns: 1fr; }}
      .chart-card {{ min-height: 340px; }}
      .chart-wrap {{ height: 252px; }}
      .chart-card.tall .chart-wrap {{ height: 272px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="eyebrow">NPS | E-commerce</div>
      <h1>Historico mensal de NPS com leitura por canal, dispositivo e categoria</h1>
      <p>
        A base foi consolidada a partir dos arquivos mensais em <strong>dados_brutos/</strong>, com remoção de duplicatas exatas,
        padronizacao de tipos e criacao de um historico unico para acompanhar tendencia e comparativos entre meses.
      </p>
      <div class="meta">
        <div class="pill">Periodo: __PERIODO_INICIO__ a __PERIODO_FIM__</div>
        <div class="pill">Arquivos: __ARQUIVOS__</div>
        <div class="pill">Atualizado em: __GERADO_EM__</div>
      </div>
    </header>

    <section class="section">
      <h2>Kpis do mes mais recente</h2>
      <div class="kpis">
        <div class="kpi">
          <div class="label">Respostas no mes mais recente</div>
          <div class="value">__RESPOSTAS__</div>
          <div class="note">Variação vs mes anterior: __DELTA_RESPOSTAS__</div>
        </div>
        <div class="kpi">
          <div class="label">NPS do mes mais recente</div>
          <div class="value">__NPS__</div>
          <div class="note">Variação vs mes anterior: __DELTA_NPS__</div>
        </div>
        <div class="kpi">
          <div class="label">Promoters</div>
          <div class="value">__PROMOTERS__</div>
          <div class="note">Notas 9 e 10.</div>
        </div>
        <div class="kpi">
          <div class="label">Detractors</div>
          <div class="value">__DETRACTORS__</div>
          <div class="note">Notas de 0 a 6.</div>
        </div>
        <div class="kpi">
          <div class="label">Ticket medio do mes</div>
          <div class="value">__TICKET__</div>
          <div class="note">Variação vs mes anterior: __DELTA_TICKET__</div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Leituras que importam</h2>
      <div class="insights">
        <div class="insight">
          <div class="tag">Melhor leitura</div>
          <div id="best-channel"></div>
          <ul id="best-channel-details"></ul>
        </div>
        <div class="insight">
          <div class="tag">Ponto de atenção</div>
          <div id="worst-channel"></div>
          <ul id="worst-channel-details"></ul>
        </div>
        <div class="insight">
          <div class="tag">Mudanca mais visivel</div>
          <div id="month-move"></div>
          <ul id="month-move-details"></ul>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Historico e segmentos</h2>
      <div class="grid">
        <article class="chart-card">
          <h3>NPS subiu, caiu ou ficou estavel ao longo dos meses?</h3>
          <p>Serie historica do NPS consolidado por mes.</p>
          <div class="chart-wrap"><canvas id="chart-nps-trend"></canvas></div>
        </article>
        <article class="chart-card">
          <h3>Composicao do NPS mudou entre promoters, passives e detractors?</h3>
          <p>Participacao percentual por mes.</p>
          <div class="chart-wrap"><canvas id="chart-composition"></canvas></div>
        </article>
        <article class="chart-card tall">
          <h3>Qual canal entrega melhor experiencia no mes mais recente?</h3>
          <p>NPS por canal na fotografia mais atual.</p>
          <div class="chart-wrap"><canvas id="chart-canal"></canvas></div>
        </article>
        <article class="chart-card tall">
          <h3>Qual dispositivo concentra a melhor e a pior leitura?</h3>
          <p>NPS por dispositivo no mes mais recente.</p>
          <div class="chart-wrap"><canvas id="chart-dispositivo"></canvas></div>
        </article>
        <article class="chart-card tall">
          <h3>Quais categorias puxam o NPS para cima ou para baixo?</h3>
          <p>NPS por categoria de compra no mes mais recente.</p>
          <div class="chart-wrap"><canvas id="chart-categoria"></canvas></div>
        </article>
        <article class="chart-card">
          <h3>Comparativo por primeiro pedido mostra onde a recorrencia muda a leitura</h3>
          <p>NPS por tipo de cliente no mes mais recente.</p>
          <div class="chart-wrap"><canvas id="chart-primeiro"></canvas></div>
        </article>
      </div>
    </section>

    <section class="section">
      <h2>Resumo mensal</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Mes</th>
              <th>Respostas</th>
              <th>NPS</th>
              <th>Promoters</th>
              <th>Passives</th>
              <th>Detractors</th>
              <th>Ticket medio</th>
            </tr>
          </thead>
          <tbody id="monthly-table"></tbody>
        </table>
      </div>
      <div class="footnote">
        NPS = percentual de promoters (notas 9 e 10) menos percentual de detractors (0 a 6). O dashboard usa a base tratada e consolidada
        em <strong>dados_tratados/nps_ecommerce_tratado.csv</strong>.
      </div>
    </section>
  </div>

  <script>
    const DADOS = {payload};
    const fmtNum = (value) => new Intl.NumberFormat('pt-BR').format(value);
    const fmtPct = (value) => new Intl.NumberFormat('pt-BR', {{ maximumFractionDigits: 1 }}).format(value) + '%';
    const fmtMoney = (value) => new Intl.NumberFormat('pt-BR', {{ style: 'currency', currency: 'BRL', minimumFractionDigits: 2 }}).format(value);
    const fmtSigned = (value, digits = 1) => {{
      const sign = value > 0 ? '+' : '';
      return sign + new Intl.NumberFormat('pt-BR', {{ minimumFractionDigits: digits, maximumFractionDigits: digits }}).format(value);
    }};
    const colors = {{
      primary: '#0f766e',
      blue: '#2563eb',
      green: '#15803d',
      orange: '#d97706',
      red: '#c2410c',
      slate: '#64748b',
      light: '#cbd5e1',
    }};

    function horizontalOptions() {{
      return {{
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            backgroundColor: '#102033',
            titleColor: '#fff',
            bodyColor: '#fff',
            padding: 12
          }}
        }},
        scales: {{
          x: {{ grid: {{ color: '#e7edf3' }}, ticks: {{ color: '#607084' }} }},
          y: {{ grid: {{ display: false }}, ticks: {{ color: '#607084' }} }}
        }}
      }};
    }}

    function renderTopSegment(titleId, detailsId, item, label, valueLabel) {{
      const title = document.getElementById(titleId);
      const details = document.getElementById(detailsId);
      if (!item) {{
        title.textContent = 'Sem dados suficientes.';
        details.innerHTML = '';
        return;
      }}
      title.innerHTML = `<strong>${{item[label]}}</strong> lidera com NPS de <strong>${{fmtNum(item.nps)}}</strong>.`;
      details.innerHTML = [
        `<li>Respostas: <strong>${{fmtNum(item.respostas)}}</strong></li>`,
        `<li>Promoters: <strong>${{fmtPct(item.promoters_pct)}}</strong></li>`,
        `<li>Detractors: <strong>${{fmtPct(item.detractors_pct)}}</strong></li>`,
        `<li>Ticket medio: <strong>${{fmtMoney(item.avg_ticket)}}</strong></li>`
      ].join('');
    }}

    const current = DADOS.current_month;
    const previous = DADOS.previous_month;

    document.getElementById('best-channel').innerHTML = current ? `O melhor canal no mes mais recente foi <strong>${{DADOS.segments.canal[0].canal}}</strong>.` : 'Sem dados.';
    document.getElementById('worst-channel').innerHTML = current ? `O canal com pior leitura foi <strong>${{DADOS.segments.canal[DADOS.segments.canal.length - 1].canal}}</strong>.` : 'Sem dados.';
    document.getElementById('month-move').innerHTML = previous
      ? `O NPS mudou <strong>${{fmtSigned(DADOS.insights.delta_nps, 1)}}</strong> p.p. no ultimo mes consolidado.`
      : 'Nao ha mes anterior para comparacao.';

    const bestChannel = DADOS.segments.canal[0];
    const worstChannel = DADOS.segments.canal[DADOS.segments.canal.length - 1];
    const bestCategory = DADOS.segments.categoria_compra[0];
    const worstCategory = DADOS.segments.categoria_compra[DADOS.segments.categoria_compra.length - 1];

    document.getElementById('best-channel-details').innerHTML = bestChannel ? [
      `<li>NPS: <strong>${{fmtNum(bestChannel.nps)}}</strong></li>`,
      `<li>Respostas: <strong>${{fmtNum(bestChannel.respostas)}}</strong></li>`,
      `<li>Ticket medio: <strong>${{fmtMoney(bestChannel.avg_ticket)}}</strong></li>`
    ].join('') : '';

    document.getElementById('worst-channel-details').innerHTML = worstChannel ? [
      `<li>NPS: <strong>${{fmtNum(worstChannel.nps)}}</strong></li>`,
      `<li>Respostas: <strong>${{fmtNum(worstChannel.respostas)}}</strong></li>`,
      `<li>Ticket medio: <strong>${{fmtMoney(worstChannel.avg_ticket)}}</strong></li>`
    ].join('') : '';

    document.getElementById('month-move-details').innerHTML = previous ? [
      `<li>Respostas: <strong>${{fmtSigned(DADOS.insights.delta_respostas, 0)}}</strong></li>`,
      `<li>Ticket medio: <strong>${{fmtSigned(DADOS.insights.delta_avg_ticket, 2)}}</strong></li>`,
      `<li>Melhor categoria: <strong>${{bestCategory.categoria_compra}}</strong> com NPS de ${{fmtNum(bestCategory.nps)}}</li>`,
      `<li>Pior categoria: <strong>${{worstCategory.categoria_compra}}</strong> com NPS de ${{fmtNum(worstCategory.nps)}}</li>`
    ].join('') : [
      `<li>Sem comparativo mensal ainda.</li>`
    ].join('');

    document.getElementById('monthly-table').innerHTML = DADOS.monthly.map(item => `
      <tr>
        <td>${{item.mes_label}}</td>
        <td>${{fmtNum(item.respostas)}}</td>
        <td>${{fmtNum(item.nps)}}</td>
        <td>${{fmtPct(item.promoters_pct)}}</td>
        <td>${{fmtPct(item.passives_pct)}}</td>
        <td>${{fmtPct(item.detractors_pct)}}</td>
        <td>${{fmtMoney(item.avg_ticket)}}</td>
      </tr>
    `).join('');

    new Chart(document.getElementById('chart-nps-trend'), {{
      type: 'line',
      data: {{
        labels: DADOS.monthly.map(item => item.mes_label),
        datasets: [{{
          label: 'NPS',
          data: DADOS.monthly.map(item => item.nps),
          tension: 0.35,
          borderColor: colors.primary,
          backgroundColor: 'rgba(15,118,110,.12)',
          pointRadius: 4,
          pointBackgroundColor: colors.primary,
          fill: true
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            backgroundColor: '#102033',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {{
              label: (ctx) => ` NPS: ${{fmtNum(ctx.parsed.y)}}`
            }}
          }}
        }},
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ color: '#607084' }} }},
          y: {{ grid: {{ color: '#e7edf3' }}, ticks: {{ color: '#607084' }} }}
        }}
      }}
    }});

    new Chart(document.getElementById('chart-composition'), {{
      type: 'bar',
      data: {{
        labels: DADOS.monthly_share.map(item => item.mes_label),
        datasets: [
          {{ label: 'Promoters', data: DADOS.monthly_share.map(item => item.promoters_pct), backgroundColor: colors.green, stack: 'stack1', borderRadius: 8 }},
          {{ label: 'Passives', data: DADOS.monthly_share.map(item => item.passives_pct), backgroundColor: colors.orange, stack: 'stack1', borderRadius: 8 }},
          {{ label: 'Detractors', data: DADOS.monthly_share.map(item => item.detractors_pct), backgroundColor: colors.red, stack: 'stack1', borderRadius: 8 }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ position: 'bottom', labels: {{ usePointStyle: true, boxWidth: 10, color: '#334155' }} }},
          tooltip: {{
            backgroundColor: '#102033',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {{
              label: (ctx) => ` ${{ctx.dataset.label}}: ${{fmtPct(ctx.parsed.y)}}`
            }}
          }}
        }},
        scales: {{
          x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#607084' }} }},
          y: {{ stacked: true, beginAtZero: true, max: 100, grid: {{ color: '#e7edf3' }}, ticks: {{ color: '#607084', callback: (value) => `${{value}}%` }} }}
        }}
      }}
    }});

    function renderSegmentChart(canvasId, itens, titleKey, color) {{
      new Chart(document.getElementById(canvasId), {{
        type: 'bar',
        data: {{
          labels: itens.map(item => item[titleKey]),
          datasets: [{{
            data: itens.map(item => item.nps),
            backgroundColor: itens.map((_, idx) => idx === 0 ? color : '#dbeafe'),
            borderRadius: 10,
            maxBarThickness: 42
          }}]
        }},
        options: {{
          ...horizontalOptions(),
          plugins: {{
            ...horizontalOptions().plugins,
            tooltip: {{
              ...horizontalOptions().plugins.tooltip,
              callbacks: {{
                label: (ctx) => ` NPS: ${{fmtNum(ctx.parsed.x)}}`
              }}
            }}
          }},
          scales: {{
            x: {{ beginAtZero: true, grid: {{ color: '#e7edf3' }}, ticks: {{ color: '#607084' }} }},
            y: {{ grid: {{ display: false }}, ticks: {{ color: '#607084' }} }}
          }}
        }}
      }});
    }}

    renderSegmentChart('chart-canal', DADOS.segments.canal, 'canal', colors.primary);
    renderSegmentChart('chart-dispositivo', DADOS.segments.dispositivo, 'dispositivo', colors.blue);
    renderSegmentChart('chart-categoria', DADOS.segments.categoria_compra, 'categoria_compra', colors.orange);
    renderSegmentChart('chart-primeiro', DADOS.segments.primeiro_pedido, 'primeiro_pedido', colors.green);
  </script>
</body>
</html>"""

    html = html.replace("__PERIODO_INICIO__", dados["metadata"]["period_start"])
    html = html.replace("__PERIODO_FIM__", dados["metadata"]["period_end"])
    html = html.replace("__ARQUIVOS__", ", ".join(dados["metadata"]["source_files"]))
    html = html.replace("__GERADO_EM__", dados["metadata"]["generated_at"])
    html = html.replace("__RESPOSTAS__", fmt_num_py(dados["current_month"]["respostas"]))
    html = html.replace("__DELTA_RESPOSTAS__", fmt_signed_py(dados["insights"]["delta_respostas"], 0))
    html = html.replace("__NPS__", fmt_num_py(dados["current_month"]["nps"]))
    html = html.replace("__DELTA_NPS__", fmt_signed_py(dados["insights"]["delta_nps"], 1))
    html = html.replace("__PROMOTERS__", fmt_pct_py(dados["current_month"]["promoters_pct"]))
    html = html.replace("__DETRACTORS__", fmt_pct_py(dados["current_month"]["detractors_pct"]))
    html = html.replace("__TICKET__", fmt_money_py(dados["current_month"]["avg_ticket"]))
    html = html.replace("__DELTA_TICKET__", fmt_signed_py(dados["insights"]["delta_avg_ticket"], 2))
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera dashboard HTML do NPS e-commerce.")
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=Path("dados_tratados") / "nps_ecommerce_tratado.csv",
        help="CSV consolidado tratado",
    )
    parser.add_argument(
        "--output-html",
        type=Path,
        default=Path("dashboards") / "dashboard_nps_ecommerce.html",
        help="Arquivo HTML de saida",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv, sep=";")
    dados = montar_dados(df)
    html = render_html(dados)

    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(html, encoding="utf-8")
    print(f"Dashboard salvo em: {args.output_html}")


if __name__ == "__main__":
    main()

from datetime import datetime
import json
import requests


def obter_historico_moeda(moeda):
    # Busca histórico recente (30 dias para base)
    url_hist = (
        f"https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/30"
    )
    resp = requests.get(url_hist).json()

    # Ordena do mais antigo para o mais recente
    resp.reverse()

    cotacao_atual = float(resp[-1]["bid"])

    # Dados para gráfico por Dia (últimos 7 dias)
    dias_labels = [
        datetime.fromtimestamp(int(d["timestamp"])).strftime("%d/%m")
        for d in resp[-7:]
    ]
    dias_values = [round(float(d["bid"]), 2) for d in resp[-7:]]

    # Dados para gráfico por Semana (médias de 4 semanas de 7 dias)
    semanas_labels = ["Sem 1", "Sem 2", "Sem 3", "Sem 4"]
    semanas_values = []
    for i in range(0, 28, 7):
        bloco = resp[i : i + 7]
        if bloco:
            media = sum(float(d["bid"]) for d in bloco) / len(bloco)
            semanas_values.append(round(media, 2))

    # Dados para gráfico por Mês (amostra dos últimos pontos)
    meses_labels = ["Mês -2", "Mês -1", "Mês Atual"]
    m1 = sum(float(d["bid"]) for d in resp[:10]) / 10
    m2 = sum(float(d["bid"]) for d in resp[10:20]) / 10
    m3 = sum(float(d["bid"]) for d in resp[20:]) / len(resp[20:])
    meses_values = [round(m1, 2), round(m2, 2), round(m3, 2)]

    # Média geral de 30 dias para cálculo do sinal
    precos_fechamento = [float(d["bid"]) for d in resp]
    media_periodo = sum(precos_fechamento) / len(precos_fechamento)

    limiar_compra = media_periodo * 0.985
    limiar_venda = media_periodo * 1.015

    if cotacao_atual <= limiar_compra:
        sinal = "🟢 COMPRA"
        classe_sinal = "buy"
        dica = "Preço abaixo da média recente. Boa oportunidade."
    elif cotacao_atual >= limiar_venda:
        sinal = "🔴 VENDA"
        classe_sinal = "sell"
        dica = "Preço valorizado. Momento favorável para venda."
    else:
        sinal = "🟡 NEUTRO"
        classe_sinal = "neutral"
        dica = "Preço dentro da média dos últimos 30 dias."

    variacao = float(resp[-1].get("pctChange", 0))

    return {
        "codigo": moeda,
        "nome": (
            "Dólar"
            if moeda == "USD"
            else ("Euro" if moeda == "EUR" else "Libra")
        ),
        "valor": f"R$ {cotacao_atual:.2f}",
        "media": f"R$ {media_periodo:.2f}",
        "sinal": sinal,
        "classe": classe_sinal,
        "dica": dica,
        "variacao": f"{variacao:+.2f}%",
        "chart_data": {
            "dias": {"labels": dias_labels, "values": dias_values},
            "semanas": {"labels": semanas_labels, "values": semanas_values},
            "meses": {"labels": meses_labels, "values": meses_values},
        },
    }


def gerar_html():
    moedas = ["USD", "EUR", "GBP"]
    dados = [obter_historico_moeda(m) for m in moedas]
    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y às %H:%M")

    cards_html = ""
    for d in dados:
        chart_data_json = json.dumps(d["chart_data"])
        cards_html += f"""
        <div class="card {d['classe']}">
            <div class="card-header">
                <h2>{d['nome']} ({d['codigo']})</h2>
                <span class="badge">{d['sinal']}</span>
            </div>
            <div class="price">{d['valor']} <span class="var">{d['variacao']}</span></div>
            <p class="media">Média 30 dias: {d['media']}</p>
            <p class="dica">{d['dica']}</p>
            
            <!-- Controles do Gráfico -->
            <div class="chart-controls">
                <button class="btn-time active" onclick="mudarPeriodo('{d['codigo']}', 'dias', this)">Dia</button>
                <button class="btn-time" onclick="mudarPeriodo('{d['codigo']}', 'semanas', this)">Semana</button>
                <button class="btn-time" onclick="mudarPeriodo('{d['codigo']}', 'meses', this)">Mês</button>
            </div>
            
            <div class="chart-container">
                <canvas id="chart-{d['codigo']}"></canvas>
            </div>
        </div>
        <script>
            window.chartData = window.chartData || {{}};
            window.chartData['{d['codigo']}'] = {chart_data_json};
        </script>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvestingWeb - Finanças e Cotações</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-card: #1e293b;
            --accent-blue: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-main);
            margin: 0;
            padding: 0;
        }}
        /* Menu Horizontal */
        header {{
            background: #1e293b;
            border-bottom: 1px solid #334155;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        nav {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 2rem;
        }}
        .logo {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent-blue);
            text-decoration: none;
        }}
        .nav-links {{
            display: flex;
            list-style: none;
            gap: 1.5rem;
            margin: 0;
            padding: 0;
        }}
        .nav-links a {{
            color: var(--text-main);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
        }}
        .nav-links a:hover, .nav-links a.active {{
            color: var(--accent-blue);
            background: #334155;
        }}

        /* Conteúdo Principal */
        main {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}
        .title-section {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}
        .title-section h1 {{
            color: var(--accent-blue);
            margin-bottom: 0.5rem;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        /* Cards e Gráficos */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
        }}
        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
            border-top: 4px solid var(--text-muted);
        }}
        .card.buy {{ border-color: #22c55e; }}
        .card.sell {{ border-color: #ef4444; }}
        .card.neutral {{ border-color: #eab308; }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card-header h2 {{ margin: 0; font-size: 1.25rem; }}
        .badge {{
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-weight: bold;
            font-size: 0.75rem;
            background: #334155;
        }}
        .price {{ font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }}
        .var {{ font-size: 0.9rem; color: #cbd5e1; font-weight: normal; }}
        .media {{ font-size: 0.85rem; color: var(--text-muted); margin: 0; }}
        .dica {{ font-size: 0.85rem; color: #cbd5e1; line-height: 1.4; margin: 0.5rem 0 1rem; }}

        /* Controles dos Gráficos */
        .chart-controls {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            background: #0f172a;
            padding: 4px;
            border-radius: 8px;
        }}
        .btn-time {{
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.4rem;
            font-size: 0.8rem;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-time.active {{
            background: var(--accent-blue);
            color: #0f172a;
        }}
        .chart-container {{
            position: relative;
            height: 180px;
            width: 100%;
        }}
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="#" class="logo">InvestingWeb</a>
            <ul class="nav-links">
                <li><a href="#" class="active">Mercados</a></li>
                <li><a href="#">Notícias</a></li>
                <li><a href="#">Aulas</a></li>
                <li><a href="#">Análises</a></li>
                <li><a href="#">Corretoras</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <div class="title-section">
            <h1>Monitor de Moedas e Cotações</h1>
            <p class="subtitle">Análise técnica em tempo real • Atualizado em {ultima_atualizacao}</p>
        </div>

        <div class="grid">
            {cards_html}
        </div>
    </main>

    <script>
        const charts = {{}};

        function inicializarGraficos() {{
            const moedas = ['USD', 'EUR', 'GBP'];
            
            moedas.forEach(m => {{
                const ctx = document.getElementById(`chart-${{m}}`).getContext('2d');
                const dataInicial = window.chartData[m]['dias'];
                
                charts[m] = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: dataInicial.labels,
                        datasets: [{{
                            label: 'Cotação (R$)',
                            data: dataInicial.values,
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3,
                            pointRadius: 3
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            x: {{ grid: {{ color: '#334155' }}, ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }} }},
                            y: {{ grid: {{ color: '#334155' }}, ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }} }}
                        }}
                    }}
                }});
            }});
        }}

        function mudarPeriodo(moeda, periodo, elementoBtn) {{
            // Atualiza botões ativos
            const parent = elementoBtn.parentElement;
            parent.querySelectorAll('.btn-time').forEach(btn => btn.classList.remove('active'));
            elementoBtn.classList.add('active');

            // Atualiza o gráfico
            const novosDados = window.chartData[moeda][periodo];
            const chart = charts[moeda];
            
            chart.data.labels = novosDados.labels;
            chart.data.datasets[0].data = novosDados.values;
            chart.update();
        }}

        document.addEventListener('DOMContentLoaded', inicializarGraficos);
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    gerar_html()
    print("Página index.html com gráficos e menu atualizada com sucesso!")
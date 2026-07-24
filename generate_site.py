import os
import json
from datetime import datetime, timezone, timedelta
import requests

# ------------------------------------------------------------------
# 1. Configurações e Coleta de Dados (AwesomeAPI)
# ------------------------------------------------------------------

CURRENCIES = ['USD', 'EUR', 'GBP']
MOEDA_NOMES = {'USD': 'Dólar', 'EUR': 'Euro', 'GBP': 'Libra'}

def fetch_currency_data(symbol):
    """Busca cotação atual e histórico dos últimos 30 dias na AwesomeAPI."""
    try:
        # Cotação Atual
        url_last = f"https://economia.awesomeapi.com.br/json/last/{symbol}-BRL"
        resp_last = requests.get(url_last, timeout=10).json()[f"{symbol}BRL"]
        price = float(resp_last['bid'])
        pct_change = float(resp_last['pctChange'])

        # Histórico (30 registros diários)
        url_daily = f"https://economia.awesomeapi.com.br/json/daily/{symbol}-BRL/30"
        resp_daily = requests.get(url_daily, timeout=10).json()
        
        # Inverte para ordem cronológica (antigo -> novo)
        history_prices = [float(item['bid']) for item in reversed(resp_daily)]
        history_dates = [
            datetime.fromtimestamp(int(item['timestamp']), tz=timezone.utc).strftime('%d/%m')
            for item in reversed(resp_daily)
        ]

        # Análise Técnica: Média Móvel de 30 dias e Sinais
        avg_30 = sum(history_prices) / len(history_prices) if history_prices else price
        
        if price < avg_30 * 0.98:
            signal_code = "buy"
            signal_label = "🟢 COMPRA"
            dica = f"Preço abaixo da média de 30 dias (R$ {avg_30:.2f}). Oportunidade técnica."
        elif price > avg_30 * 1.02:
            signal_code = "sell"
            signal_label = "🔴 VENDA"
            dica = f"Preço acima da média de 30 dias (R$ {avg_30:.2f}). Atenção para correção."
        else:
            signal_code = "neutral"
            signal_label = "🟡 NEUTRO"
            dica = "Preço negociado dentro da média dos últimos 30 dias."

        # Estrutura de dados para o Chart.js
        chart_data = {
            "dias": {
                "labels": history_dates[-7:],
                "values": [round(v, 2) for v in history_prices[-7:]]
            },
            "semanas": {
                "labels": ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
                "values": [
                    round(sum(history_prices[i:i+7])/len(history_prices[i:i+7]), 2) 
                    for i in range(0, min(28, len(history_prices)), 7)
                ]
            },
            "meses": {
                "labels": ["Mês -2", "Mês -1", "Mês Atual"],
                "values": [
                    round(sum(history_prices[:10])/10, 2),
                    round(sum(history_prices[10:20])/10, 2),
                    round(sum(history_prices[20:])/len(history_prices[20:]), 2)
                ]
            }
        }

        return {
            "symbol": symbol,
            "nome": MOEDA_NOMES.get(symbol, symbol),
            "price": f"{price:.2f}",
            "pctChange": f"{pct_change:+.2f}%",
            "avg_30": f"{avg_30:.2f}",
            "signal_code": signal_code,
            "signal_label": signal_label,
            "dica": dica,
            "chartData": chart_data
        }

    except Exception as e:
        print(f"Erro ao buscar dados para {symbol}: {e}")
        # Retorno fallback para testes
        return {
            "symbol": symbol,
            "nome": MOEDA_NOMES.get(symbol, symbol),
            "price": "5.00",
            "pctChange": "0.00%",
            "avg_30": "5.00",
            "signal_code": "neutral",
            "signal_label": "🟡 NEUTRO",
            "dica": "Dados temporariamente indisponíveis.",
            "chartData": {"dias": {"labels": [], "values": []}, "semanas": {"labels": [], "values": []}, "meses": {"labels": [], "values": []}}
        }

# ------------------------------------------------------------------
# 2. Templates HTML
# ------------------------------------------------------------------

HTML_HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvestingWeb - Finanças e Cotações</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-card: #1e293b;
            --accent-blue: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }

        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg-primary); color: var(--text-main); margin: 0; padding: 0; }
        header { background: #1e293b; border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; }
        nav { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.5rem; }
        .logo { font-size: 1.5rem; font-weight: bold; color: var(--accent-blue); text-decoration: none; }
        .nav-links { display: flex; list-style: none; gap: 1rem; margin: 0; padding: 0; }
        .nav-links a { color: var(--text-main); text-decoration: none; font-weight: 500; transition: color 0.2s, background 0.2s; padding: 0.5rem 0.75rem; border-radius: 6px; }
        .nav-links a:hover, .nav-links a.active { color: var(--accent-blue); background: var(--border-color); }
        main { max-width: 1200px; margin: 1.5rem auto; padding: 0 1.5rem; }
        .title-section { text-align: center; margin-bottom: 2rem; }
        .title-section h1 { color: var(--accent-blue); margin-bottom: 0.5rem; }
        .subtitle { color: var(--text-muted); font-size: 0.9rem; }

        /* Calculadora */
        .converter-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        .converter-card h3 { margin: 0 0 0.75rem 0; font-size: 1.05rem; color: var(--accent-blue); }
        .converter-grid { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; }
        .converter-field { flex: 1; min-width: 110px; }
        .converter-field label { display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem; font-weight: bold; }
        .converter-input, .converter-select { width: 100%; padding: 0.5rem; background: #0f172a; border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-main); font-size: 0.9rem; box-sizing: border-box; }
        .converter-input:focus, .converter-select:focus { outline: none; border-color: var(--accent-blue); }
        .converter-result { flex: 1.2; min-width: 150px; background: #0f172a; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--border-color); text-align: center; }
        .converter-result-label { font-size: 0.75rem; color: var(--text-muted); display: block; }
        .converter-result-value { font-size: 1.1rem; font-weight: bold; color: #22c55e; }

        /* Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; }
        .card { background: var(--bg-card); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); border-top: 4px solid var(--text-muted); }
        .card.buy { border-color: #22c55e; }
        .card.sell { border-color: #ef4444; }
        .card.neutral { border-color: #eab308; }
        .card-header { display: flex; justify-content: space-between; align-items: center; }
        .card-header h2 { margin: 0; font-size: 1.25rem; }
        .badge { padding: 0.25rem 0.6rem; border-radius: 9999px; font-weight: bold; font-size: 0.75rem; background: var(--border-color); }
        .price { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
        .var { font-size: 0.9rem; color: #cbd5e1; font-weight: normal; }
        .media { font-size: 0.85rem; color: var(--text-muted); margin: 0; }
        .dica { font-size: 0.85rem; color: #cbd5e1; line-height: 1.4; margin: 0.5rem 0 1rem; }
        .chart-controls { display: flex; gap: 0.5rem; margin-bottom: 1rem; background: #0f172a; padding: 4px; border-radius: 8px; }
        .btn-time { flex: 1; background: transparent; border: none; color: var(--text-muted); padding: 0.4rem; font-size: 0.8rem; font-weight: bold; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
        .btn-time.active { background: var(--accent-blue); color: #0f172a; }
        .chart-container { position: relative; height: 180px; width: 100%; }

        /* Rodapé / Marca d'água */
        .watermark-footer { width: 100%; text-align: center; padding: 2.5rem 0 1.5rem 0; margin-top: 3rem; border-top: 1px solid rgba(51, 65, 85, 0.4); }
        .watermark-text { font-size: 1.5rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: var(--text-muted); opacity: 0.25; user-select: none; }
    </style>
</head>
<body>
"""

def generate_header(active_page):
    pages = {
        "index.html": "Mercados",
        "noticias.html": "Notícias",
        "aulas.html": "Aulas",
        "analises.html": "Análises",
        "corretoras.html": "Corretoras"
    }
    nav_items = ""
    for file, label in pages.items():
        active_class = ' class="active"' if file == active_page else ''
        nav_items += f'<li><a href="{file}"{active_class}>{label}</a></li>\n'

    return f"""
    <header>
        <nav>
            <a href="index.html" class="logo">InvestingWeb</a>
            <ul class="nav-links">
                {nav_items}
            </ul>
        </nav>
    </header>
"""

FOOTER_HTML = """
    <footer class="watermark-footer">
        <span class="watermark-text">InvestingWeb</span>
    </footer>
</body>
</html>
"""

# ------------------------------------------------------------------
# 3. Geradores de Cada Página
# ------------------------------------------------------------------

def render_index(data_list):
    # Fuso horário do Brasil (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_br).strftime('%d/%m/%Y às %H:%M')
    
    cards_html = ""
    for d in data_list:
        cards_html += f"""
        <div class="card {d['signal_code']}">
            <div class="card-header">
                <h2>{d['nome']} ({d['symbol']})</h2>
                <span class="badge">{d['signal_label']}</span>
            </div>
            <div class="price">R$ {d['price']} <span class="var">{d['pctChange']}</span></div>
            <p class="media">Média 30 dias: R$ {d['avg_30']}</p>
            <p class="dica">{d['dica']}</p>
            
            <div class="chart-controls">
                <button class="btn-time active" onclick="mudarPeriodo('{d['symbol']}', 'dias', this)">Dia</button>
                <button class="btn-time" onclick="mudarPeriodo('{d['symbol']}', 'semanas', this)">Semana</button>
                <button class="btn-time" onclick="mudarPeriodo('{d['symbol']}', 'meses', this)">Mês</button>
            </div>
            
            <div class="chart-container">
                <canvas id="chart-{d['symbol']}"></canvas>
            </div>
        </div>
        <script>
            window.chartData = window.chartData || {{}};
            window.chartData['{d['symbol']}'] = {json.dumps(d['chartData'])};
        </script>
        """

    content = f"""
    <main>
        <div class="title-section">
            <h1>Monitor de Moedas e Cotações</h1>
            <p class="subtitle">Análise técnica em tempo real • Atualizado em {agora}</p>
        </div>

        <section class="converter-card">
            <h3>Calculadora de Conversão</h3>
            <div class="converter-grid">
                <div class="converter-field">
                    <label for="calc-amount">Valor</label>
                    <input type="number" id="calc-amount" class="converter-input" value="1" min="0" step="any">
                </div>
                <div class="converter-field">
                    <label for="calc-from">De</label>
                    <select id="calc-from" class="converter-select">
                        <option value="BRL">BRL (Real)</option>
                        <option value="USD">USD (Dólar)</option>
                        <option value="EUR">EUR (Euro)</option>
                        <option value="GBP">GBP (Libra)</option>
                    </select>
                </div>
                <div class="converter-field">
                    <label for="calc-to">Para</label>
                    <select id="calc-to" class="converter-select">
                        <option value="USD">USD (Dólar)</option>
                        <option value="BRL" selected>BRL (Real)</option>
                        <option value="EUR">EUR (Euro)</option>
                        <option value="GBP">GBP (Libra)</option>
                    </select>
                </div>
                <div class="converter-result">
                    <span class="converter-result-label">Resultado Convertido</span>
                    <span id="calc-result" class="converter-result-value">R$ 0,00</span>
                </div>
            </div>
        </section>

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
            const parent = elementoBtn.parentElement;
            parent.querySelectorAll('.btn-time').forEach(btn => btn.classList.remove('active'));
            elementoBtn.classList.add('active');

            const novosDados = window.chartData[moeda][periodo];
            const chart = charts[moeda];
            
            chart.data.labels = novosDados.labels;
            chart.data.datasets[0].data = novosDados.values;
            chart.update();
        }}

        document.addEventListener('DOMContentLoaded', inicializarGraficos);
    </script>
    <script src="calculator.js"></script>
    """
    return HTML_HEAD + generate_header("index.html") + content + FOOTER_HTML

# ------------------------------------------------------------------
# 4. Execução Principal
# ------------------------------------------------------------------

def main():
    print("Iniciando geração do site InvestingWeb...")
    
    # 1. Coleta dados para o Index
    currency_data = [fetch_currency_data(symbol) for symbol in CURRENCIES]

    # 2. Gera e salva o index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(render_index(currency_data))
    print("✓ index.html gerado com sucesso.")

    print("Gerador finalizado. Todos os arquivos foram atualizados!")

if __name__ == "__main__":
    main()
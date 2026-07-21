import os
from datetime import datetime
import requests


def obter_dados_moeda(moeda):
    # Busca cotação atual e histórico recente (últimos 30 dias)
    url_atual = f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL"
    url_historico = (
        f"https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/30"
    )

    resp_atual = requests.get(url_atual).json()[f"{moeda}BRL"]
    resp_hist = requests.get(url_historico).json()

    cotacao_atual = float(resp_atual["bid"])

    # Calcula a média dos últimos 30 dias
    precos_fechamento = [float(dia["bid"]) for dia in resp_hist]
    media_periodo = sum(precos_fechamento) / len(precos_fechamento)

    # Regra simples: 1.5% abaixo da média = Compra | 1.5% acima = Venda
    limiar_compra = media_periodo * 0.985
    limiar_venda = media_periodo * 1.015

    if cotacao_atual <= limiar_compra:
        sinal = "🟢 COMPRA"
        classe_sinal = "buy"
        dica = "Preço abaixo da média recente. Boa oportunidade de compra."
    elif cotacao_atual >= limiar_venda:
        sinal = "🔴 VENDA"
        classe_sinal = "sell"
        dica = "Preço valorizado. Momento favorável para venda."
    else:
        sinal = "🟡 NEUTRO"
        classe_sinal = "neutral"
        dica = "Preço dentro da média dos últimos 30 dias."

    return {
        "nome": resp_atual["name"].split("/")[0],
        "valor": f"R$ {cotacao_atual:.2f}",
        "media": f"R$ {media_periodo:.2f}",
        "sinal": sinal,
        "classe": classe_sinal,
        "dica": dica,
        "variacao": f"{float(resp_atual['pctChange']):+.2f}%",
    }


def gerar_html():
    moedas = ["USD", "EUR", "GBP"]
    dados = [obter_dados_moeda(m) for m in moedas]
    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y às %H:%M")

    cards_html = ""
    for d in dados:
        cards_html += f"""
        <div class="card {d['classe']}">
            <h2>{d['nome']}</h2>
            <div class="price">{d['valor']} <span class="var">{d['variacao']}</span></div>
            <p class="media">Média 30 dias: {d['media']}</p>
            <div class="badge">{d['sinal']}</div>
            <p class="dica">{d['dica']}</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Finanças - Cotações & Sinais</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
        h1 {{ text-align: center; color: #38bdf8; margin-bottom: 0.5rem; }}
        p.subtitle {{ text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 2rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; max-width: 1000px; margin: 0 auto; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); border-top: 4px solid #94a3b8; }}
        .card.buy {{ border-color: #22c55e; }}
        .card.sell {{ border-color: #ef4444; }}
        .card.neutral {{ border-color: #eab308; }}
        .price {{ font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }}
        .var {{ font-size: 0.9rem; color: #cbd5e1; font-weight: normal; }}
        .media {{ font-size: 0.85rem; color: #94a3b8; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: bold; font-size: 0.85rem; margin: 1rem 0 0.5rem; background: #334155; }}
        .dica {{ font-size: 0.85rem; color: #cbd5e1; line-height: 1.4; }}
    </style>
</head>
<body>
    <h1>Painel de Cotações</h1>
    <p class="subtitle">Análise automatizada de moedas • Atualizado em {ultima_atualizacao}</p>
    <div class="grid">
        {cards_html}
    </div>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    gerar_html()
    print("Página index.html gerada com sucesso!")
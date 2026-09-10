// Taxas base em relação ao BRL
let exchangeRates = {
    "BRL": 1.0,
    "USD": 5.20,
    "EUR": 5.60,
    "GBP": 6.50
};

// Buscar cotações atualizadas em tempo real via AwesomeAPI
async function fetchLatestRates() {
    try {
        const response = await fetch('https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL');
        const data = await response.json();
        
        exchangeRates["USD"] = parseFloat(data.USDBRL.bid);
        exchangeRates["EUR"] = parseFloat(data.EURBRL.bid);
        exchangeRates["GBP"] = parseFloat(data.GBPBRL.bid);

        calculateConversion(); // Recalcula assim que atualizar as taxas
    } catch (error) {
        console.error("Erro ao carregar taxas para a calculadora:", error);
    }
}

function calculateConversion() {
    const amountInput = document.getElementById('calc-amount');
    const selectFrom = document.getElementById('calc-from');
    const selectTo = document.getElementById('calc-to');
    const resultElement = document.getElementById('calc-result');

    if (!amountInput || !selectFrom || !selectTo || !resultElement) return;

    const amount = parseFloat(amountInput.value) || 0;
    const fromCurrency = selectFrom.value;
    const toCurrency = selectTo.value;

    // Converte o valor de origem para BRL (moeda base)
    const amountInBRL = amount * exchangeRates[fromCurrency];

    // Converte de BRL para a moeda de destino
    const convertedAmount = amountInBRL / exchangeRates[toCurrency];

    // Formatação de moeda no padrão local
    const formattedResult = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: toCurrency
    }).format(convertedAmount);

    resultElement.innerText = formattedResult;
}

// Função para buscar cotações ao vivo da AwesomeAPI e atualizar o index
async function carregarCotacoesAoVivo() {
    try {
        const resposta = await fetch('https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL');
        const dados = await resposta.json();

        const moedas = {
            'USD': dados.USDBRL,
            'EUR': dados.EURBRL,
            'GBP': dados.GBPBRL
        };

        // Atualiza cada card na tela dinamicamente
        for (const [sigla, info] of Object.entries(moedas)) {
            const precoCard = document.getElementById(`preco-${sigla}`);

            if (precoCard && info) {
                const valor = parseFloat(info.bid).toFixed(2);
                const variacao = parseFloat(info.pctChange);
                const varFormatada = (variacao >= 0 ? '+' : '') + variacao.toFixed(2) + '%';

                // Atualiza o texto do preço
                precoCard.innerHTML = `R$ ${valor} `;
                
                // Reaplica a tag de variação estilizada
                const spanVar = document.createElement('span');
                spanVar.className = 'var';
                spanVar.textContent = varFormatada;
                
                // Cor da variação (verde se positivo, vermelho se negativo)
                spanVar.style.color = variacao >= 0 ? '#22c55e' : '#ef4444';
                
                precoCard.appendChild(spanVar);
            }
        }

        // Atualiza a data/hora no topo para o momento atual
        const agora = new Date().toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
        const subelement = document.querySelector('.subtitle');
        if (subelement) {
            subelement.innerHTML = `Análise técnica em tempo real • Atualizado em ${agora.replace(',', ' às')}`;
        }

    } catch (erro) {
        console.error("Erro ao carregar cotações ao vivo:", erro);
    }
}

// Configuração dos Event Listeners e Inicialização quando o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    const amountInput = document.getElementById('calc-amount');
    const selectFrom = document.getElementById('calc-from');
    const selectTo = document.getElementById('calc-to');

    if (amountInput) amountInput.addEventListener('input', calculateConversion);
    if (selectFrom) selectFrom.addEventListener('change', calculateConversion);
    if (selectTo) selectTo.addEventListener('change', calculateConversion);

    // Executa as buscas e cálculos iniciais
    fetchLatestRates();
    carregarCotacoesAoVivo();
});
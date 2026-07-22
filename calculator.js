// Taxas base em relação ao BRL (Substitua ou atualize dinamicamente via API)
let exchangeRates = {
    "BRL": 1.0,
    "USD": 5.20, // Exemplo: 1 USD = 5.20 BRL
    "EUR": 5.60, // Exemplo: 1 EUR = 5.60 BRL
    "GBP": 6.50  // Exemplo: 1 GBP = 6.50 BRL
};

// Opcional: Buscar cotações atualizadas em tempo real via AwesomeAPI no JS
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
    const amount = parseFloat(document.getElementById('calc-amount').value) || 0;
    const fromCurrency = document.getElementById('calc-from').value;
    const toCurrency = document.getElementById('calc-to').value;

    // Converte o valor de origem para BRL (moeda base)
    const amountInBRL = amount * exchangeRates[fromCurrency];

    // Converte de BRL para a moeda de destino
    const convertedAmount = amountInBRL / exchangeRates[toCurrency];

    // Formatação de moeda no padrão local
    const formattedResult = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: toCurrency
    }).format(convertedAmount);

    document.getElementById('calc-result').innerText = formattedResult;
}

// Event Listeners para calcular automaticamente ao alterar qualquer campo
document.getElementById('calc-amount').addEventListener('input', calculateConversion);
document.getElementById('calc-from').addEventListener('change', calculateConversion);
document.getElementById('calc-to').addEventListener('change', calculateConversion);

// Inicialização
fetchLatestRates();
calculateConversion();
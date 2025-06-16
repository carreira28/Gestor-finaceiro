let deferredPrompt;
let rendimentos = 0;
let despesas = 0;

/*BD*/
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js')
    .then(() => console.log('Service Worker registado com sucesso.'))
    .catch((error) => console.log('Erro ao registar o Service Worker:', error));
}

// Popup de definições
const btnDefinicoes = document.getElementById('btn-definicoes');
const popup = document.getElementById('popup-definicoes');
const fecharPopup = document.getElementById('fechar-popup');

btnDefinicoes.addEventListener('click', () => {
  popup.style.display = 'block';
});

fecharPopup.addEventListener('click', () => {
  popup.style.display = 'none';
});

window.addEventListener('click', (event) => {
  if (event.target == popup) {
    popup.style.display = 'none';
  }
});

// Inicialização do gráfico — só se o canvas existir
const canvasGrafico = document.getElementById('grafico-financas');
let grafico = null;

if (canvasGrafico) {
  const ctx = canvasGrafico.getContext('2d');
  grafico = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Rendimentos', 'Despesas', 'Poupanças'],
      datasets: [{
        label: 'Valores em €',
        data: [0, 0, 0],  // Dados iniciais para o gráfico
        backgroundColor: ['#28a745', '#dc3545', '#17a2b8'],
        borderColor: ['#218838', '#c82333', '#138496'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

function adicionarRendimento() {
  const rendimentoInput = document.getElementById('rendimento');
  const valorRendimento = parseFloat(rendimentoInput.value);
  
  if (!isNaN(valorRendimento)) {
    rendimentos += valorRendimento;
    atualizarRendimentos();
    rendimentoInput.value = '';
    atualizarPoupancas();
    atualizarGrafico();  // Atualiza o gráfico só se existir
  }
}

function adicionarDespesa() {
  const despesaInput = document.getElementById('despesa');
  const valorDespesa = parseFloat(despesaInput.value);
  
  if (!isNaN(valorDespesa)) {
    despesas += valorDespesa;
    atualizarDespesas();
    despesaInput.value = '';
    atualizarPoupancas();
    atualizarGrafico();  // Atualiza o gráfico só se existir
  }
}

function atualizarRendimentos() {
  const listaRendimentos = document.getElementById('lista-rendimentos');
  const itemRendimento = document.createElement('li');
  itemRendimento.textContent = `Rendimento: ${rendimentos.toFixed(2)}€`;
  listaRendimentos.appendChild(itemRendimento);
}

function atualizarDespesas() {
  const listaDespesas = document.getElementById('lista-despesas');
  const itemDespesa = document.createElement('li');
  itemDespesa.textContent = `Despesa: ${despesas.toFixed(2)}€`;
  listaDespesas.appendChild(itemDespesa);
}

function atualizarPoupancas() {
  const poupancas = rendimentos - despesas;
  document.getElementById('poupancas-valor').textContent = `Poupanças: ${poupancas.toFixed(2)}€`;
}

function atualizarGrafico() {
  if (!grafico) return; // Sai se o gráfico não existir para evitar erro
  const poupancas = rendimentos - despesas;
  grafico.data.datasets[0].data = [rendimentos, despesas, poupancas];
  grafico.update();
}

const btnDownloadPdf = document.getElementById('btn-download-pdf');
if (btnDownloadPdf) {
  btnDownloadPdf.addEventListener('click', () => {
    const canvas = document.getElementById('grafico-financas');
    if (!canvas) return;

    const imagem = canvas.toDataURL('image/png', 1.0);

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();

    const larguraPDF = 180;
    const alturaPDF = (canvas.height * larguraPDF) / canvas.width;

    pdf.setFontSize(18);
    pdf.text("Gráfico do Resumo Financeiro Mensal", 15, 20);
    pdf.addImage(imagem, 'PNG', 15, 30, larguraPDF, alturaPDF);
    pdf.save("grafico-financas.pdf");
  });
}

// Código para instalar o PWA
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;

  const installButton = document.getElementById('install-button');
  installButton.style.display = 'block';

  installButton.addEventListener('click', () => {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('Usuário aceitou o prompt de instalação');
      } else {
        console.log('Usuário rejeitou o prompt de instalação');
      }
      deferredPrompt = null;
    });
  });
});

// Animação de carregamento
document.addEventListener('DOMContentLoaded', function() {
  const progressRing = document.querySelector('.ring-progress');
  const circumference = 2 * Math.PI * 54;
  let progress = 0;
  
  progressRing.style.strokeDasharray = circumference;
  progressRing.style.strokeDashoffset = circumference;
  
  const interval = setInterval(() => {
    progress += 1;
    const offset = circumference - (progress / 100) * circumference;
    progressRing.style.strokeDashoffset = offset;
    
    if (progress >= 100) {
      clearInterval(interval);
      setTimeout(() => {
        document.getElementById('loading-screen').classList.add('fade-out');
      }, 500);
    }
  }, 30);
  
  const currencyContainer = document.querySelector('.currency-animation');
  for (let i = 0; i < 15; i++) {
    const currency = document.createElement('span');
    currency.innerHTML = ['€'][Math.floor(Math.random() * 1)];
    currency.style.left = `${Math.random() * 100}%`;
    currency.style.animationDelay = `${Math.random() * 1}s`;
    currency.style.animationDuration = `${6 + Math.random() * 7}s`;
    currencyContainer.appendChild(currency);
  }
});

// Registrar o Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('service-worker.js')
    .then((registration) => {
      console.log('Service Worker registrado com sucesso:', registration);
    })
    .catch((error) => {
      console.error('Erro ao registrar o Service Worker:', error);
    });
}

// Definições
async function aplicarCores() {
    const corTexto = document.getElementById('corTexto').value;
    const corHeader = document.getElementById('corHeader').value;
    
    // Aplicar imediatamente
    document.querySelectorAll('.nome-utilizador, .titulo').forEach(el => {
        el.style.color = corTexto;
    });
    document.querySelector('header').style.backgroundColor = corHeader;
    
    try {
        const response = await fetch('/salvar_cores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `cor_titulo=${encodeURIComponent(corTexto)}&cor_header=${encodeURIComponent(corHeader)}`
        });
        
        const data = await response.json();
        if (!data.success) {
            console.error('Erro ao salvar:', data.error || 'Erro desconhecido');
            alert('Erro ao salvar: ' + (data.error || 'Tente novamente'));
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão');
    }
}

// Carregar cores ao iniciar
document.addEventListener('DOMContentLoaded', function() {
    const corSalvaTitulo = "{{ cor_titulo }}";
    const corSalvaHeader = "{{ cor_header }}";
    
    if (corSalvaTitulo) {
        document.querySelectorAll('.nome-utilizador, .titulo').forEach(el => {
            el.style.color = corSalvaTitulo;
        });
        document.getElementById('corTexto').value = corSalvaTitulo;
    }
    
    if (corSalvaHeader) {
        document.querySelector('header').style.backgroundColor = corSalvaHeader;
        document.getElementById('corHeader').value = corSalvaHeader;
    }
});

document.getElementById('btn-limpar').addEventListener('click', () => {
  if (confirm("Tem a certeza que deseja limpar todos os dados e reiniciar?")) {
    rendimentos = 0;
    despesas = 0;

    document.getElementById('lista-rendimentos').innerHTML = '';
    document.getElementById('lista-despesas').innerHTML = '';
    document.getElementById('poupancas-valor').textContent = 'Poupanças: 0.00€';

    atualizarGrafico();
    location.reload(); 
  }
});

//Relogio
document.documentElement.style.setProperty('--cor-titulo', '{{ cor_titulo }}');
function atualizarDataHora() {
  const agora = new Date();
  const dia = agora.getDate().toString().padStart(2, '0');
  const mes = (agora.getMonth() + 1).toString().padStart(2, '0');
  const ano = agora.getFullYear();
  const horas = agora.getHours().toString().padStart(2, '0');
  const minutos = agora.getMinutes().toString().padStart(2, '0');
  const segundos = agora.getSeconds().toString().padStart(2, '0');
  
  document.getElementById("data-hora").textContent = `${dia}/${mes}/${ano} - ${horas}:${minutos}:${segundos}`;
}

setInterval(atualizarDataHora, 1000);
atualizarDataHora();

    const stock = {};

    function atualizarLista() {
      const lista = document.getElementById('lista-stock');
      lista.innerHTML = '';
      for (const produto in stock) {
        const item = document.createElement('li');
        item.textContent = `${produto} → ${stock[produto]} unidades`;
        lista.appendChild(item);
      }
    }

    function adicionarEntrada() {
      const nome = document.getElementById('produto-entrada').value.trim();
      const qtd = parseInt(document.getElementById('quantidade-entrada').value);

      if (nome && !isNaN(qtd)) {
        if (!stock[nome]) stock[nome] = 0;
        stock[nome] += qtd;
        atualizarLista();
      }

      document.getElementById('produto-entrada').value = '';
      document.getElementById('quantidade-entrada').value = '';
    }

    function adicionarSaida() {
      const nome = document.getElementById('produto-saida').value.trim();
      const qtd = parseInt(document.getElementById('quantidade-saida').value);

      if (nome && !isNaN(qtd)) {
        if (!stock[nome]) stock[nome] = 0;
        stock[nome] -= qtd;
        atualizarLista();
      }

      document.getElementById('produto-saida').value = '';
      document.getElementById('quantidade-saida').value = '';
    }
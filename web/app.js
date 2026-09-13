const state = { dossier: null };

const ratioRoot = document.querySelector('#ratios');
const riskRoot = document.querySelector('#risks');
const tickerForm = document.querySelector('#ticker-form');
const tickerInput = document.querySelector('#ticker');
const companyRoot = document.querySelector('#company');
const statusRoot = document.querySelector('#run-status');
const tickerLabel = document.querySelector('#ticker-label');
const tickerPrice = document.querySelector('#ticker-price');
const tickerChange = document.querySelector('#ticker-change');
const capitalRoot = document.querySelector('#capital-matrix');
let requestSequence = 0;

function renderDossier(data) {
  state.dossier = data;
  companyRoot.innerHTML = `${data.company} <em>${data.ticker}</em>`;
  tickerLabel.textContent = `LIVE · ${data.ticker}`;
  tickerPrice.textContent = typeof data.price === 'number' ? `$${data.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : data.price;
  tickerChange.textContent = `${data.change >= 0 ? '+' : ''}${Number(data.change).toFixed(2)}%`;
  capitalRoot.innerHTML = data.capital_matrix.map((row) => `<tr><td>${row.metric}</td><td>${row.current}</td><td>${row.prior}</td><td class="table-delta">${row.delta}</td></tr>`).join('');
  ratioRoot.innerHTML = data.ratios.map((ratio) => `
    <article class="ratio-card tone-${ratio.tone}">
      <span class="ratio-label">${ratio.label}</span>
      <strong class="ratio-value">${ratio.value}</strong>
      <span class="ratio-detail">${ratio.detail}</span>
    </article>`).join('');
  riskRoot.innerHTML = data.risk_vectors.map((risk) => `
    <article class="risk-item">
      <header><h3>${risk.title}</h3><span class="severity ${risk.severity === 'LOW' ? 'low' : ''}">${risk.severity}</span></header>
      <p>${risk.text}</p>
    </article>`).join('');
}

async function loadDossier(ticker = tickerInput.value) {
  ticker = ticker.trim().toUpperCase();
  if (!ticker) return;
  const sequence = ++requestSequence;
  const response = await fetch(`/api/dossier?ticker=${encodeURIComponent(ticker)}`);
  if (!response.ok) throw new Error('Dossier unavailable');
  const data = await response.json();
  if (sequence === requestSequence) renderDossier(data);
}

function traceTicker(ticker) {
  statusRoot.textContent = '● ANALYZING';
  const stream = new EventSource(`/api/stream?ticker=${encodeURIComponent(ticker)}`);
  stream.onmessage = (event) => {
    const trace = JSON.parse(event.data);
    statusRoot.textContent = trace.step === 'complete' ? '● COMPLETE' : `● ${trace.step.toUpperCase()}`;
    if (trace.step === 'complete') stream.close();
  };
  stream.onerror = () => { stream.close(); statusRoot.textContent = '● OFFLINE'; };
}

tickerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  tickerInput.value = tickerInput.value.toUpperCase();
  try {
    await loadDossier(tickerInput.value);
    traceTicker(tickerInput.value);
  } catch (error) {
    statusRoot.textContent = '● ERROR';
    ratioRoot.innerHTML = '<p class="subtitle">Ticker lookup failed. Check the symbol or data connection.</p>';
  }
});

document.querySelector('#refresh').addEventListener('click', async (event) => {
  event.currentTarget.textContent = '↻ Loading...';
  await loadDossier(tickerInput.value);
  event.currentTarget.textContent = '↻ Refresh data';
});

document.querySelectorAll('.nav-item').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    document.querySelectorAll('.dashboard').forEach((view) => view.classList.add('hidden'));
    document.querySelector(`#${button.dataset.view}-view`).classList.remove('hidden');
  });
});

loadDossier().catch(() => {
  ratioRoot.innerHTML = '<p class="subtitle">API unavailable. Start the server with python app.py.</p>';
});

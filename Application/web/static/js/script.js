document.addEventListener('DOMContentLoaded', () => {
  // 1) Fetch symbols for dropdown
  fetch('/api/symbols')
    .then(res => res.json())
    .then(symbols => {
      populateDropdown(symbols);
    })
    .catch(err => console.error('Error fetching symbols:', err));

  // 2) Load Data button logic
  const loadDataBtn = document.getElementById('loadDataBtn');
  loadDataBtn.addEventListener('click', () => {
    const symbol = document.getElementById('symbolDropdown').value;
    fetchMarketData(symbol);
  });
});

function populateDropdown(symbols) {
  const dropdown = document.getElementById('symbolDropdown');
  dropdown.innerHTML = '';
  symbols.forEach(sym => {
    const option = document.createElement('option');
    option.value = sym;
    option.text = sym;
    dropdown.appendChild(option);
  });
}

function fetchMarketData(symbol) {
  fetch(`/api/market-data/${symbol}`)
    .then(res => res.json())
    .then(data => {
      renderTable(data);
      renderChart(data, symbol);
      fetchKnnSignals(symbol); // Fetch KNN signals and add to chart
    })
    .catch(err => console.error('Error fetching market data:', err));
}


function fetchKnnSignals(symbol) {
  fetch(`/api/knn-signals/${symbol}`)
  .then(response => {
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
  })
  .then(signals => addSignalsToChart(signals))
  .catch(err => console.error('Error fetching KNN signals:', err));
}

function addSignalsToChart(signals) {
  const offset = 5; // Adjust this value as needed for vertical spacing

  const buyMarkers = {
      x: signals.filter(s => s.type === 'buy').map(s => s.date),
      y: signals.filter(s => s.type === 'buy').map(s => s.price + offset), // Move buy markers up
      mode: 'markers',
      marker: { color: 'green', symbol: 'triangle-up', size: 12 },
      name: 'Buy Signals'
  };

  const sellMarkers = {
      x: signals.filter(s => s.type === 'sell').map(s => s.date),
      y: signals.filter(s => s.type === 'sell').map(s => s.price - offset), // Move sell markers down
      mode: 'markers',
      marker: { color: 'red', symbol: 'triangle-down', size: 12 },
      name: 'Sell Signals'
  };

  // Add markers to the existing chart
  Plotly.addTraces('chartContainer', [buyMarkers, sellMarkers]);
}



// -------------- Table Rendering --------------

function renderTable(data) {
  const tableBody = document.querySelector('#marketDataTable tbody');
  tableBody.innerHTML = ''; // clear existing rows

  data.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.date}</td>
      <td>${formatNumber(row.open)}</td>
      <td>${formatNumber(row.high)}</td>
      <td>${formatNumber(row.low)}</td>
      <td>${formatNumber(row.close)}</td>
      <td>${row.volume ?? ''}</td>
      <td>${formatNumber(row.ema_8)}</td>
      <td>${formatNumber(row.ema_13)}</td>
      <td>${formatNumber(row.ema_21)}</td>
      <td>${formatNumber(row.ema_34)}</td>
      <td>${formatNumber(row.ema_55)}</td>
      <td>${formatNumber(row.ema_89)}</td>
      <td>${formatNumber(row.ema_144)}</td>
      <td>${formatNumber(row.ema_200)}</td>
      <td>${row.signals}</td>
    `;
    tableBody.appendChild(tr);
  });
}

// Helper to format numbers to 2 decimal places or blank if null
function formatNumber(val) {
  return (val !== null && val !== undefined) ? val.toFixed(2) : '';
}

// -------------- Chart Rendering (Plotly) --------------
function renderChart(data, symbol) {
  // 1) Prepare arrays
  const dates = data.map(d => d.date);
  const open = data.map(d => d.open);
  const high = data.map(d => d.high);
  const low = data.map(d => d.low);
  const close = data.map(d => d.close);

  // 2) Candlestick trace
  const candlestickTrace = {
    x: dates,
    open: open,
    high: high,
    low: low,
    close: close,
    type: 'candlestick',
    name: `${symbol} Price`,
    increasing: { line: { color: 'green' } },
    decreasing: { line: { color: 'red' } }
  };

  // 3) Create a trace for each EMA
  //    We'll do line plots for them
  function lineTrace(name, values, color) {
    return {
      x: dates,
      y: values,
      type: 'scatter',
      mode: 'lines',
      name: name,
      line: { color: color }
    };
  }

  // A single variable controlling the color & transparency for all EMAs:
const EMA_COLOR = 'rgba(255, 0, 0, 0.25)'; // red at 50% opacity


  const ema8Trace   = lineTrace('EMA_8',   data.map(d => d.ema_8),   EMA_COLOR);
  const ema13Trace  = lineTrace('EMA_13',  data.map(d => d.ema_13),  EMA_COLOR);
  const ema21Trace  = lineTrace('EMA_21',  data.map(d => d.ema_21),  EMA_COLOR);
  const ema34Trace  = lineTrace('EMA_34',  data.map(d => d.ema_34),  EMA_COLOR);
  const ema55Trace  = lineTrace('EMA_55',  data.map(d => d.ema_55),  EMA_COLOR);
  const ema89Trace  = lineTrace('EMA_89',  data.map(d => d.ema_89),  EMA_COLOR);
  const ema144Trace = lineTrace('EMA_144', data.map(d => d.ema_144), EMA_COLOR);
  const ema200Trace = lineTrace('EMA_200', data.map(d => d.ema_200), EMA_COLOR);

  // 4) Combine all traces
  const traces = [
    candlestickTrace,
    ema8Trace,
    ema13Trace,
    ema21Trace,
    ema34Trace,
    ema55Trace,
    ema89Trace,
    ema144Trace,
    ema200Trace
  ];

  // 5) Layout (e.g. dark background or normal)
  const layout = {
    title: `${symbol} Price + EMA Ribbon`,
    xaxis: { title: 'Date' },
    yaxis: { title: 'Price' },
    // If you prefer a dark theme:
    paper_bgcolor: '#1e1e1e',
    plot_bgcolor: '#1e1e1e',
    font: { color: '#ffffff' },
  };

  // 6) Plot
  Plotly.newPlot('chartContainer', traces, layout);
}

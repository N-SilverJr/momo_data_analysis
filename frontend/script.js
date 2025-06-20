let transactions = [];
let charts = {};
let isChartsInitialized = false;

// Debounce utility to prevent rapid filter requests
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Fetch transaction data from API
async function fetchData(params = {}) {
  try {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`http://localhost:5000/api/transactions?${query}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`HTTP ${response.status}: ${errorData.error || 'Unknown error'}`);
    }
    transactions = await response.json();
    try {
      if (!isChartsInitialized) {
        renderCharts();
        isChartsInitialized = true;
      } else {
        updateCharts(transactions);
      }
      renderTable(transactions);
    } catch (error) {
      console.error('Error rendering charts or table:', error);
      alert(`Failed to render data: ${error.message}`);
    }
  } catch (error) {
    console.error('Error fetching data:', error);
    alert(`Failed to load transaction data: ${error.message}`);
  }
}

// Format date for display
function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// Initialize charts
function renderCharts() {
  console.log('Initializing charts');
  // Destroy existing charts
  if (charts.volumeByType) {
    console.log('Destroying volumeByType chart');
    charts.volumeByType.destroy();
  }
  if (charts.monthlySummary) {
    console.log('Destroying monthlySummary chart');
    charts.monthlySummary.destroy();
  }
  if (charts.paymentDistribution) {
    console.log('Destroying paymentDistribution chart');
    charts.paymentDistribution.destroy();
  }

  // Transaction volume by type (bar chart)
  const volumeByTypeCtx = document.getElementById('volume-by-type').getContext('2d');
  const typeCounts = transactions.reduce((acc, t) => {
    acc[t.transaction_type] = (acc[t.transaction_type] || 0) + 1;
    return acc;
  }, {});
  charts.volumeByType = new Chart(volumeByTypeCtx, {
    type: 'bar',
    data: {
      labels: Object.keys(typeCounts),
      datasets: [{
        label: 'Number of Transactions',
        data: Object.values(typeCounts),
        backgroundColor: '#004aad',
        borderColor: '#003080',
        borderWidth: 1
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Count' } },
        x: { title: { display: true, text: 'Transaction Type' } }
      }
    }
  });
  console.log('Created volumeByType chart');

  // Monthly summaries (line chart)
  const monthlySummaryCtx = document.getElementById('monthly-summary').getContext('2d');
  const monthlyData = transactions.reduce((acc, t) => {
    const date = new Date(t.timestamp);
    if (!isNaN(date)) {
      const month = date.toLocaleString('en-US', { year: 'numeric', month: 'short' });
      acc[month] = (acc[month] || 0) + (t.amount || 0);
    }
    return acc;
  }, {});
  charts.monthlySummary = new Chart(monthlySummaryCtx, {
    type: 'line',
    data: {
      labels: Object.keys(monthlyData),
      datasets: [{
        label: 'Total Amount (RWF)',
        data: Object.values(monthlyData),
        borderColor: '#004aad',
        backgroundColor: 'rgba(0, 74, 173, 0.2)',
        fill: true
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Amount (RWF)' } },
        x: { title: { display: true, text: 'Month' } }
      }
    }
  });
  console.log('Created monthlySummary chart');

  // Payment/deposit distribution (pie chart)
  const paymentDistCtx = document.getElementById('payment-distribution').getContext('2d');
  const paymentTypes = ['payment', 'incoming', 'bank_deposit'];
  const paymentCounts = paymentTypes.map(type =>
    transactions.filter(t => t.transaction_type === type).reduce((sum, t) => sum + (t.amount || 0), 0)
  );
  charts.paymentDistribution = new Chart(paymentDistCtx, {
    type: 'pie',
    data: {
      labels: ['Payments', 'Incoming', 'Bank Deposits'],
      datasets: [{
        data: paymentCounts,
        backgroundColor: ['#004aad', '#28a745', '#ffc107'],
        borderColor: '#fff',
        borderWidth: 1
      }]
    },
    options: {
      plugins: { legend: { position: 'right' } }
    }
  });
  console.log('Created paymentDistribution chart');
}

// Update charts with filtered data
function updateCharts(filtered) {
  console.log('Updating charts with new data');
  // Update volume by type
  const typeCounts = filtered.reduce((acc, t) => {
    acc[t.transaction_type] = (acc[t.transaction_type] || 0) + 1;
    return acc;
  }, {});
  charts.volumeByType.data.labels = Object.keys(typeCounts);
  charts.volumeByType.data.datasets[0].data = Object.values(typeCounts);
  charts.volumeByType.update();
  console.log('Updated volumeByType chart');

  // Update monthly summaries
  const monthlyData = filtered.reduce((acc, t) => {
    const date = new Date(t.timestamp);
    if (!isNaN(date)) {
      const month = date.toLocaleString('en-US', { year: 'numeric', month: 'short' });
      acc[month] = (acc[month] || 0) + (t.amount || 0);
    }
    return acc;
  }, {});
  charts.monthlySummary.data.labels = Object.keys(monthlyData);
  charts.monthlySummary.data.datasets[0].data = Object.values(monthlyData);
  charts.monthlySummary.update();
  console.log('Updated monthlySummary chart');

  // Update payment/deposit distribution
  const paymentTypes = ['payment', 'incoming', 'bank_deposit'];
  const paymentCounts = paymentTypes.map(type =>
    filtered.filter(t => t.transaction_type === type).reduce((sum, t) => sum + (t.amount || 0), 0)
  );
  charts.paymentDistribution.data.datasets[0].data = paymentCounts;
  charts.paymentDistribution.update();
  console.log('Updated paymentDistribution chart');
}

// Render transaction table
function renderTable(data) {
  const tbody = document.getElementById('transaction-list');
  tbody.innerHTML = '';
  if (data.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="8">No transactions match the filters.</td>`;
    tbody.appendChild(row);
    return;
  }
  data.forEach(t => {
    const date = new Date(t.timestamp);
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${t.message_id}</td>
      <td>${!isNaN(date) ? formatDate(t.timestamp) : '-'}</td>
      <td>${t.transaction_type}</td>
      <td>${t.amount ? t.amount.toLocaleString() : '-'}</td>
      <td>${t.recipient || '-'}</td>
      <td>${t.reference || '-'}</td>
      <td>${t.balance ? t.balance.toLocaleString() : '-'}</td>
      <td>${t.status}</td>
    `;
    tbody.appendChild(row);
  });
}

// Apply filters
const debouncedApplyFilters = debounce(function () {
  const params = {};
  const typeFilter = document.getElementById('type-filter').value;
  const dateStart = document.getElementById('date-start').value;
  const dateEnd = document.getElementById('date-end').value;
  const amountMin = document.getElementById('amount-min').value;
  const amountMax = document.getElementById('amount-max').value;

  if (typeFilter) params.type = typeFilter;
  if (dateStart) params.date_start = dateStart;
  if (dateEnd) params.date_end = dateEnd;
  if (amountMin && !isNaN(parseInt(amountMin))) params.amount_min = parseInt(amountMin);
  if (amountMax && !isNaN(parseInt(amountMax))) params.amount_max = parseInt(amountMax);

  console.log('Applying filters with params:', params);
  fetchData(params);
}, 300);

// Event listeners
document.getElementById('apply-filters').addEventListener('click', debouncedApplyFilters);

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, fetching initial data');
  fetchData();
});
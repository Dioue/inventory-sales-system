// Define datasets
let batchData = {};
let batchChartData = {};
let batchChart;  // Declare it here so it's accessible outside

fetch('/api/batch-volume/')
  .then(res => res.json())
  .then(data => {
    // Prepare data
    batchData = {
      today: {
        total: `${formatNumber(data.today.total)}`,
        range: "Batch Volume",
        change: `${data.today.change > 0 ? '+' : ''}${data.today.change}%`,
        changePositive: data.today.changePositive,
      },
      last7Days: {
        total: formatNumber(data.last7Days.total),
        range: "Batch Volume",
        change: `${data.last7Days.change > 0 ? '+' : ''}${data.last7Days.change}%`,
        changePositive: data.last7Days.changePositive,
      },
      last30Days: {
        total: formatNumber(data.last30Days.total),
        range: "Batch Volume",
        change: `${data.last30Days.change > 0 ? '+' : ''}${data.last30Days.change}%`,
        changePositive: data.last30Days.changePositive,
      },
    };

    batchChartData = {
      today: {
        series: [{ name: 'Batch', data: data.today.data }],
        xaxis: { categories: data.today.dates },
      },
      last7Days: {
        series: [{ name: 'Batch', data: data.last7Days.data }],
        xaxis: { categories: data.last7Days.dates },
      },
      last30Days: {
        series: [{ name: 'Batch', data: data.last30Days.data }],
        xaxis: { categories: data.last30Days.dates },
      },
    };

    const batchOptions = {
      chart: {
        type: 'area',
        height: 200,
        toolbar: {
          show: true,
          tools: {
            pan: false,
          },
        },
      },
      dataLabels: { enabled: false },
      series: batchChartData.last7Days.series,
      xaxis: {
        type: 'datetime',
        categories: batchChartData.last7Days.xaxis.categories,
        labels: {
          formatter: function (value) {
            return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          },
        },
      },
    };

    batchChart = new ApexCharts(document.getElementById("batch-chart"), batchOptions);
    batchChart.render();

    updateBatchData(batchData.last7Days);
  })
  .catch(error => console.error('Error fetching batch data:', error));

document.querySelectorAll('#lastDaysdropdown_batch a').forEach((dropdownItem) => {
  dropdownItem.addEventListener('click', (event) => {
    event.preventDefault();
    const text = dropdownItem.textContent.trim();

    // Update batchChart
    if (text === 'Today') {
      batchChart.updateOptions(batchChartData.today);
      updateBatchData(batchData.today);
    } else if (text === 'Last 7 days') {
      batchChart.updateOptions(batchChartData.last7Days);
      updateBatchData(batchData.last7Days);
    } else if (text === 'Last 30 days') {
      batchChart.updateOptions(batchChartData.last30Days);
      updateBatchData(batchData.last30Days);
    }

    // Update dropdown button text
    document.getElementById('dropdownDefaultButton_batch').innerHTML = `
      ${text}
      <svg class="w-2.5 m-2.5 ms-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
      </svg>`;
  });
});


// Function to update batch data
function updateBatchData(data) {
  document.getElementById('batchTotal').textContent = data.total;
  document.getElementById('batchRange').textContent = data.range;

  const batchChangeElement = document.getElementById('batchChange');
  batchChangeElement.textContent = data.change;

  const batchArrow = document.getElementById('batchArrow');

  const batchChangeContainer = document.getElementById('batchChangeContainer');
  if (data.changePositive) {
    batchChangeContainer.classList.add('text-green-500', 'dark:text-green-500');
    batchChangeContainer.classList.remove('text-red-500', 'dark:text-red-500');
    batchArrow.innerHTML = `
    <svg  class="w-3 h-3 ms-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 14">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13V1m0 0L1 5m4-4 4 4"/>
    </svg>
    `
  } else {
    batchChangeContainer.classList.add('text-red-500', 'dark:text-red-500');
    batchChangeContainer.classList.remove('text-green-500', 'dark:text-green-500');
    batchArrow.innerHTML = `
    <svg class="w-4 h-4 ms-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19V5m0 14-4-4m4 4 4-4"/>
    </svg>
    `
  }
}


function formatNumber(num) {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
}

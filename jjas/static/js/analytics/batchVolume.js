// Define datasets
let batchData = {};
let batchChartData = {};
let batchChart;  // Declare it here so it's accessible outside

fetch('/api/volume-stats/')
  .then(res => res.json())
  .then(data => {
    // Prepare data
    batchData = {
      today: {
        total: `${formatNumber(data.today.batch_total)}`,
        range: "Batch Volume",
      },
      last7Days: {
        total: formatNumber(data.last7Days.batch_total),
        range: "Batch Volume",
      },
      last30Days: {
        total: formatNumber(data.last30Days.batch_total),
        range: "Batch Volume",
      },
    };

    batchChartData = {
      today: {
        series: [{ name: 'Batch', data: data.today.batch_total }],
        xaxis: { categories: data.today.date },
      },
      last7Days: {
        series: [{ name: 'Batch', data: data.last7Days.batch_data }],
        xaxis: { categories: data.last7Days.dates },
      },
      last30Days: {
        series: [{ name: 'Batch', data: data.last30Days.batch_data }],
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
}


function formatNumber(num) {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
}

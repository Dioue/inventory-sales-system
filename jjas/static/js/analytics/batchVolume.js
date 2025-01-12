// Define datasets
const batchData = {
  today: {
    total: "1.5k",
    range: "batch today",
    change: "+8%",
    changePositive: true,
  },
  last7Days: {
    total: "32.4k",
    range: "batch this week",
    change: "+12%",
    changePositive: true,
  },
  last30Days: {
    total: "120k",
    range: "batch this month",
    change: "-5%",
    changePositive: false,
  },
};



const batchChartData = {
  today: {
    series: [{ name: 'Batches', data: [5, 6] }],
    xaxis: { categories: ['11 Jan', '12 Jan'] },
  },
  last7Days: {
    series: [{ name: 'Batches', data: [10, 15, 20, 25, 30, 35, 40] }],
    xaxis: { categories: ['06 Jan', '07 Jan', '08 Jan', '09 Jan', '10 Jan', '11 Jan', '12 Jan'] },
  },
  last30Days: {
    series: [
      {
        name: 'Batches',
        data: (() => {
          const dailyData = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155];
          const aggregatedData = [];
          for (let i = 0; i < dailyData.length; i += 7) {
            const weekData = dailyData.slice(i, i + 7);
            aggregatedData.push(weekData.reduce((sum, value) => sum + value, 0));
          }
          return aggregatedData;
        })(),
      },
    ],
    xaxis: {
      categories: (() => {
        const totalDays = 30;
        const categories = [];
        for (let i = 0; i < totalDays; i += 7) {
          const startDay = i + 1;
          const endDay = Math.min(i + 7, totalDays);
          categories.push(`${startDay}–${endDay} Jan`);
        }
        return categories;
      })(),
    },
  },
};


// Initialize the chart
const batchSaleOptions = {
  chart: { type: 'area', height: 200, 
    toolbar: {
      show: true,
      tools: {
          pan: false,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  series: batchChartData.last7Days.series, // Default to last 7 days
  xaxis: batchChartData.last7Days.xaxis,
};

const batchChart = new ApexCharts(document.getElementById("batch-chart"), batchSaleOptions);
batchChart.render();

// Update chart and batch data
document.querySelectorAll('#lastDaysdropdown_batch a').forEach((dropdownItem) => {
  dropdownItem.addEventListener('click', (event) => {
    event.preventDefault();
    const text = dropdownItem.textContent.trim();

    // Update chart
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


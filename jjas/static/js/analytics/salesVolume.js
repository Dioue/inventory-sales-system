// Define datasets
const salesData = {
    today: {
      total: "1.5k",
      range: "sales today",
      change: "+8%",
      changePositive: true,
    },
    last7Days: {
      total: "32.4k",
      range: "sales this week",
      change: "+12%",
      changePositive: true,
    },
    last30Days: {
      total: "120k",
      range: "sales this month",
      change: "-5%",
      changePositive: false,
    },
  };
  
  
  
  const salesChartData = {
    today: {
      series: [{ name: 'Sales', data: [5, 6] }],
      xaxis: { categories: ['11 Jan', '12 Jan'] },
    },
    last7Days: {
      series: [{ name: 'Sales', data: [10, 15, 20, 25, 30, 35, 40] }],
      xaxis: { categories: ['06 Jan', '07 Jan', '08 Jan', '09 Jan', '10 Jan', '11 Jan', '12 Jan'] },
    },
    last30Days: {
      series: [
        {
          name: 'Sales',
          data: (() => {
            const salesDailyData = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155];
            const aggregatedSalesData = [];
            for (let i = 0; i < salesDailyData.length; i += 7) {
              const salesWeekData = salesDailyData.slice(i, i + 7);
              aggregatedSalesData.push(salesWeekData.reduce((sum, value) => sum + value, 0));
            }
            return aggregatedSalesData;
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
  
  
  // Initialize the salesChart
  const salesOptions = {
    chart: { type: 'area', height: 150,
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
    series: salesChartData.last7Days.series, // Default to last 7 days
    xaxis: salesChartData.last7Days.xaxis,
  };
  
  const salesChart = new ApexCharts(document.getElementById("sales-chart"), salesOptions);
  salesChart.render();
  
  // Update salesChart and sales data
  document.querySelectorAll('#lastDaysdropdown_sales a').forEach((dropdownItem) => {
    dropdownItem.addEventListener('click', (event) => {
      event.preventDefault();
      const text = dropdownItem.textContent.trim();
  
      // Update salesChart
      if (text === 'Today') {
        salesChart.updateOptions(salesChartData.today);
        updateSalesData(salesData.today);
      } else if (text === 'Last 7 days') {
        salesChart.updateOptions(salesChartData.last7Days);
        updateSalesData(salesData.last7Days);
      } else if (text === 'Last 30 days') {
        salesChart.updateOptions(salesChartData.last30Days);
        updateSalesData(salesData.last30Days);
      }
  
      // Update dropdown button text
      document.getElementById('dropdownDefaultButton_sales').innerHTML = `
        ${text}
        <svg class="w-2.5 m-2.5 ms-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
        </svg>`;
    });
  });
  
  
  // Function to update sales data
  function updateSalesData(data) {
    document.getElementById('salesTotal').textContent = data.total;
    document.getElementById('salesRange').textContent = data.range;
  
    const salesChangeElement = document.getElementById('salesChange');
    salesChangeElement.textContent = data.change;
  
    const salesArrow = document.getElementById('salesArrow');
  
    const salesChangeContainer = document.getElementById('salesChangeContainer');
    if (data.changePositive) {
      salesChangeContainer.classList.add('text-green-500', 'dark:text-green-500');
      salesChangeContainer.classList.remove('text-red-500', 'dark:text-red-500');
      salesArrow.innerHTML = `
      <svg  class="w-3 h-3 ms-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 14">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13V1m0 0L1 5m4-4 4 4"/>
      </svg>
      `
    } else {
      salesChangeContainer.classList.add('text-red-500', 'dark:text-red-500');
      salesChangeContainer.classList.remove('text-green-500', 'dark:text-green-500');
      salesArrow.innerHTML = `
      <svg class="w-4 h-4 ms-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19V5m0 14-4-4m4 4 4-4"/>
      </svg>
      `
    }
  }
  
  
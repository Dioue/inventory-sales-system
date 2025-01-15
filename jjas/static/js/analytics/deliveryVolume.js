// Define datasets
const deliveryData = {
    today: {
      total: "1.5k",
      range: "delivery today",
      change: "+8%",
      changePositive: true,
    },
    last7Days: {
      total: "32.4k",
      range: "delivery this week",
      change: "+12%",
      changePositive: true,
    },
    last30Days: {
      total: "120k",
      range: "delivery this month",
      change: "-5%",
      changePositive: false,
    },
  };
  
  
  
  const deliveryChartData = {
    today: {
      series: [{ name: 'Deliveries', data: [5, 6] }],
      xaxis: { categories: ['11 Jan', '12 Jan'] },
    },
    last7Days: {
      series: [{ name: 'Deliveries', data: [10, 15, 20, 25, 30, 35, 40] }],
      xaxis: { categories: ['06 Jan', '07 Jan', '08 Jan', '09 Jan', '10 Jan', '11 Jan', '12 Jan'] },
    },
    last30Days: {
      series: [
        {
          name: 'Deliveries',
          data: (() => {
            const deliveryDailyData = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155];
            const aggregateddeliveryData = [];
            for (let i = 0; i < deliveryDailyData.length; i += 7) {
              const deliveryWeekData = deliveryDailyData.slice(i, i + 7);
              aggregateddeliveryData.push(deliveryWeekData.reduce((sum, value) => sum + value, 0));
            }
            return aggregateddeliveryData;
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
  
  
  // Initialize the deliveryChart
  const deliveryOptions = {
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
    series: deliveryChartData.last7Days.series, // Default to last 7 days
    xaxis: deliveryChartData.last7Days.xaxis,
  };
  
  const deliveryChart = new ApexCharts(document.getElementById("delivery-chart"), deliveryOptions);
  deliveryChart.render();
  
  // Update deliveryChart and delivery data
  document.querySelectorAll('#lastDaysdropdown_delivery a').forEach((dropdownItem) => {
    dropdownItem.addEventListener('click', (event) => {
      event.preventDefault();
      const text = dropdownItem.textContent.trim();
  
      // Update deliveryChart
      if (text === 'Today') {
        deliveryChart.updateOptions(deliveryChartData.today);
        updatedeliveryData(deliveryData.today);
      } else if (text === 'Last 7 days') {
        deliveryChart.updateOptions(deliveryChartData.last7Days);
        updatedeliveryData(deliveryData.last7Days);
      } else if (text === 'Last 30 days') {
        deliveryChart.updateOptions(deliveryChartData.last30Days);
        updatedeliveryData(deliveryData.last30Days);
      }
  
      // Update dropdown button text
      document.getElementById('dropdownDefaultButton_delivery').innerHTML = `
        ${text}
        <svg class="w-2.5 m-2.5 ms-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
        </svg>`;
    });
  });
  
  
  // Function to update delivery data
  function updatedeliveryData(data) {
    document.getElementById('deliveryTotal').textContent = data.total;
    document.getElementById('deliveryRange').textContent = data.range;
  
    const deliveryChangeElement = document.getElementById('deliveryChange');
    deliveryChangeElement.textContent = data.change;
  
    const deliveryArrow = document.getElementById('deliveryArrow');
  
    const deliveryChangeContainer = document.getElementById('deliveryChangeContainer');
    if (data.changePositive) {
      deliveryChangeContainer.classList.add('text-green-500', 'dark:text-green-500');
      deliveryChangeContainer.classList.remove('text-red-500', 'dark:text-red-500');
      deliveryArrow.innerHTML = `
      <svg  class="w-3 h-3 ms-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 14">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13V1m0 0L1 5m4-4 4 4"/>
      </svg>
      `
    } else {
      deliveryChangeContainer.classList.add('text-red-500', 'dark:text-red-500');
      deliveryChangeContainer.classList.remove('text-green-500', 'dark:text-green-500');
      deliveryArrow.innerHTML = `
      <svg class="w-4 h-4 ms-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19V5m0 14-4-4m4 4 4-4"/>
      </svg>
      `
    }
  }
  
  
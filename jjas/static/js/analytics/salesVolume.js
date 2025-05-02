// Define datasets
let salesData = {};
let salesChartData = {};
let salesChart;  // Declare it here so it's accessible outside

fetch('/api/sales-delivery-volume/')
  .then(res => res.json())
  .then(data => {
    // Prepare sales data for different ranges (today, last 7 days, last 30 days)
    salesData = {
      today: {
        total: `${formatNumber(data.today.total_sales)}`,
        range: "Sales Volume",
        change: `${data.today.change_sales > 0 ? '+' : ''}${data.today.change_sales}%`,
        changePositive: data.today.changePositive_sales,
      },
      last7Days: {
        total: formatNumber(data.last7Days.total_sales),
        range: "Sales Volume",
        change: `${data.last7Days.change_sales > 0 ? '+' : ''}${data.last7Days.change_sales}%`,
        changePositive: data.last7Days.changePositive_sales,
      },
      last30Days: {
        total: formatNumber(data.last30Days.total_sales),
        range: "Sales Volume",
        change: `${data.last30Days.change_sales > 0 ? '+' : ''}${data.last30Days.change_sales}%`,
        changePositive: data.last30Days.changePositive_sales,
      },
    };

    // Prepare chart data for different date ranges
    salesChartData = {
      today: {
        series: [{ name: 'Sales', data: data.today.sales_data }],
        xaxis: { categories: data.today.dates },
      },
      last7Days: {
        series: [{ name: 'Sales', data: data.last7Days.sales_data }],
        xaxis: { categories: data.last7Days.dates },
      },
      last30Days: {
        series: [{ name: 'Sales', data: data.last30Days.sales_data }],
        xaxis: { categories: data.last30Days.dates },
      },
    };

    // Initialize ApexCharts with data for the last 7 days as the default view
    const salesOptions = {
      chart: {
        type: 'area',
        height: 150,
        toolbar: {
          show: true,
          tools: {
            pan: false,
          },
        },
      },
      dataLabels: { enabled: false },
      series: salesChartData.last7Days.series,
      xaxis: {
        type: 'datetime',
        categories: salesChartData.last7Days.xaxis.categories,
        labels: {
          formatter: function (value) {
            return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          },
        },
      },
    };

    salesChart = new ApexCharts(document.getElementById("sales-chart"), salesOptions);
    salesChart.render();

    // Set initial sales data on page load
    updateSalesData(salesData.last7Days);
  })
  .catch(error => console.error('Error fetching sales data:', error));
  
  
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
  
  
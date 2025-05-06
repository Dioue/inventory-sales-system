// Define datasets
let salesData = {};
let salesChartData = {};
let salesChart;  // Declare it here so it's accessible outside

fetch('/api/volume-stats/')
  .then(res => res.json())
  .then(data => {
    // Prepare sales data for different ranges (today, last 7 days, last 30 days)
    salesData = {
      today: {
        total: `${formatNumber(data.today.sales_total)}`,
        range: "Sales Volume",
      },
      last7Days: {
        total: formatNumber(data.last7Days.sales_total),
        range: "Sales Volume",
      },
      last30Days: {
        total: formatNumber(data.last30Days.sales_total),
        range: "Sales Volume",
      },
    };

    // Prepare chart data for different date ranges
    salesChartData = {
      today: {
        series: [{ name: 'Sales', data: data.today.sales_total }],
        xaxis: { categories: data.today.date },
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
        height: 200,
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
  }
  
  
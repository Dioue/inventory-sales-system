// Define datasets
let deliveryData = {};
let deliveryChartData = {};
let deliveryChart;  // Declare it here so it's accessible outside

fetch('/api/volume-stats/')  // Update the endpoint to match the delivery data API
  .then(res => res.json())
  .then(data => {
    // Prepare data for today's, last 7 days, and last 30 days delivery data
    deliveryData = {
      today: {
        total: `${formatNumber(data.today.delivery_total)}`,  // Using total_delivery from API
        range: "Delivery Volume",
      },
      last7Days: {
        total: formatNumber(data.last7Days.delivery_total),
        range: "Delivery Volume",
      },
      last30Days: {
        total: formatNumber(data.last30Days.delivery_total),
        range: "Delivery Volume",
      },
    };

    // Prepare chart data for different date ranges
    deliveryChartData = {
      today: {
        series: [{ name: 'Deliveries', data: data.today.delivery_total }],
        xaxis: { categories: data.today.date },  // Assuming dates are in an array
      },
      last7Days: {
        series: [{ name: 'Deliveries', data: data.last7Days.delivery_data }],
        xaxis: { categories: data.last7Days.dates },
      },
      last30Days: {
        series: [{ name: 'Deliveries', data: data.last30Days.delivery_data }],
        xaxis: { categories: data.last30Days.dates },
      },
    };

    // Initialize the chart with the default "Last 7 Days" view
    const deliveryOptions = {
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
      series: deliveryChartData.last7Days.series,
      xaxis: {
        type: 'datetime',
        categories: deliveryChartData.last7Days.xaxis.categories,
        labels: {
          formatter: function (value) {
            return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          },
        },
      },
    };

    deliveryChart = new ApexCharts(document.getElementById("delivery-chart"), deliveryOptions);
    deliveryChart.render();

    // Set initial delivery data to be displayed
    updateDeliveryData(deliveryData.last7Days);
  })
  .catch(error => console.error('Error fetching delivery data:', error));
  
  // Update deliveryChart and delivery data
  document.querySelectorAll('#lastDaysdropdown_delivery a').forEach((dropdownItem) => {
    dropdownItem.addEventListener('click', (event) => {
      event.preventDefault();
      const text = dropdownItem.textContent.trim();
  
      // Update deliveryChart
      if (text === 'Today') {
        deliveryChart.updateOptions(deliveryChartData.today);
        updateDeliveryData(deliveryData.today);
      } else if (text === 'Last 7 days') {
        deliveryChart.updateOptions(deliveryChartData.last7Days);
        updateDeliveryData(deliveryData.last7Days);
      } else if (text === 'Last 30 days') {
        deliveryChart.updateOptions(deliveryChartData.last30Days);
        updateDeliveryData(deliveryData.last30Days);
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
  function updateDeliveryData(data) {
    document.getElementById('deliveryTotal').textContent = data.total;
    document.getElementById('deliveryRange').textContent = data.range;
  }
  
  
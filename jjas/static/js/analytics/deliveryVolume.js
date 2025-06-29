document.addEventListener('DOMContentLoaded', function () {
  let deliveryData = {};
  let deliveryChartData = {};
  let deliveryChart;

  fetch('/api/volume-stats/')
    .then(res => res.json())
    .then(data => {
      // Debug logs
      console.log('API response:', data);

      // Prepare delivery totals
      deliveryData = {
        today: {
          total: formatNumber(data.today.delivery_total || 0),
          range: "Delivery Volume",
        },
        last7Days: {
          total: formatNumber(data.last7Days.delivery_total || 0),
          range: "Delivery Volume",
        },
        last30Days: {
          total: formatNumber(data.last30Days.delivery_total || 0),
          range: "Delivery Volume",
        },
      };

      // Ensure data arrays exist
      deliveryChartData = {
        today: {
          series: [{ name: 'Deliveries', data: [data.today.delivery_data || 0] }],
          xaxis: { categories: [data.today.dates] || [] },
        },
        last7Days: {
          series: [{ name: 'Deliveries', data: data.last7Days.delivery_data || [] }],
          xaxis: { categories: data.last7Days.dates || [] },
        },
        last30Days: {
          series: [{ name: 'Deliveries', data: data.last30Days.delivery_data || [] }],
          xaxis: { categories: data.last30Days.dates || [] },
        },
      };

      // Setup chart options
      const deliveryOptions = {
        chart: {
          type: 'area',
          height: 200,
          toolbar: {
            show: true,
            tools: { pan: false },
          },
        },
        dataLabels: { enabled: false },
        series: deliveryChartData.last7Days.series,
        xaxis: {
          type: 'datetime',
          categories: deliveryChartData.last7Days.xaxis.categories,
          labels: {
            formatter: function (value) {
              const date = new Date(value);
              return isNaN(date) ? value : date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
              });
            }
          },
        },
      };

      // Initialize chart
      deliveryChart = new ApexCharts(document.getElementById("delivery-chart"), deliveryOptions);
      deliveryChart.render();

      // Set initial delivery display data
      updateDeliveryData(deliveryData.last7Days);
    })
    .catch(error => console.error('Error fetching delivery data:', error));

  // Dropdown handling
  document.querySelectorAll('#lastDaysdropdown_delivery a').forEach((dropdownItem) => {
    dropdownItem.addEventListener('click', (event) => {
      event.preventDefault();
      const text = dropdownItem.textContent.trim();

      let selectedData, selectedChart;
      if (text === 'Today') {
        selectedData = deliveryData.today;
        selectedChart = deliveryChartData.today;
      } else if (text === 'Last 7 days') {
        selectedData = deliveryData.last7Days;
        selectedChart = deliveryChartData.last7Days;
      } else if (text === 'Last 30 days') {
        selectedData = deliveryData.last30Days;
        selectedChart = deliveryChartData.last30Days;
      }

      if (selectedData && selectedChart) {
        deliveryChart.updateOptions({
          series: selectedChart.series,
          xaxis: {
            ...selectedChart.xaxis,
            type: 'datetime',
            labels: {
              formatter: function (value) {
                const date = new Date(value);
                return isNaN(date) ? value : date.toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric'
                });
              }
            }
          }
        });

        updateDeliveryData(selectedData);

        // Update dropdown label
        document.getElementById('dropdownDefaultButton_delivery').innerHTML = `
          ${text}
          <svg class="w-2.5 m-2.5 ms-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
          </svg>`;
      }
    });
  });

  // Utility to update delivery numbers
  function updateDeliveryData(data) {
    document.getElementById('deliveryTotal').textContent = data.total;
    document.getElementById('deliveryRange').textContent = data.range;
  }

  // Format number utility
  function formatNumber(num) {
    return Number(num || 0).toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }
});

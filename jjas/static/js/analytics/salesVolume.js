document.addEventListener('DOMContentLoaded', function () {
  let salesData = {};
  let salesChartData = {};
  let salesChart;

  fetch('/api/volume-stats/')
    .then(res => res.json())
    .then(data => {
      // Debug log
      console.log('Sales API response:', data);

      // Prepare display data
      salesData = {
        today: {
          total: formatNumber(data.today.sales_total || 0),
          range: "Sales Volume",
        },
        last7Days: {
          total: formatNumber(data.last7Days.sales_total || 0),
          range: "Sales Volume",
        },
        last30Days: {
          total: formatNumber(data.last30Days.sales_total || 0),
          range: "Sales Volume",
        },
      };

      // Prepare chart data
      salesChartData = {
        today: {
          series: [{ name: 'Sales', data: [data.today.sales_total || 0] }],
          xaxis: { categories: [data.today.date] },
        },
        last7Days: {
          series: [{ name: 'Sales', data: data.last7Days.sales_data || [] }],
          xaxis: { categories: data.last7Days.dates || [] },
        },
        last30Days: {
          series: [{ name: 'Sales', data: data.last30Days.sales_data || [] }],
          xaxis: { categories: data.last30Days.dates || [] },
        },
      };

      // Initialize chart
      const salesOptions = {
        chart: {
          type: 'area',
          height: 200,
          toolbar: {
            show: true,
            tools: { pan: false },
          },
        },
        dataLabels: { enabled: false },
        series: salesChartData.last7Days.series,
        xaxis: {
          type: 'datetime',
          categories: salesChartData.last7Days.xaxis.categories,
          labels: {
            formatter: function (value) {
              const date = new Date(value);
              return isNaN(date) ? value : date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              });
            },
          },
        },
      };

      salesChart = new ApexCharts(document.getElementById("sales-chart"), salesOptions);
      salesChart.render();

      updateSalesData(salesData.last7Days);
    })
    .catch(error => console.error('Error fetching sales data:', error));

  // Dropdown toggle
  document.querySelectorAll('#lastDaysdropdown_sales a').forEach((dropdownItem) => {
    dropdownItem.addEventListener('click', (event) => {
      event.preventDefault();
      const text = dropdownItem.textContent.trim();

      let selectedChart = null;
      let selectedData = null;

      if (text === 'Today') {
        selectedChart = salesChartData.today;
        selectedData = salesData.today;
      } else if (text === 'Last 7 days') {
        selectedChart = salesChartData.last7Days;
        selectedData = salesData.last7Days;
      } else if (text === 'Last 30 days') {
        selectedChart = salesChartData.last30Days;
        selectedData = salesData.last30Days;
      }

      if (selectedChart && selectedData) {
        salesChart.updateOptions({
          series: selectedChart.series,
          xaxis: {
            type: 'datetime',
            categories: selectedChart.xaxis.categories,
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

        updateSalesData(selectedData);

        // Update dropdown label
        document.getElementById('dropdownDefaultButton_sales').innerHTML = `
          ${text}
          <svg class="w-2.5 m-2.5 ms-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
          </svg>`;
      }
    });
  });

  // Update text data
  function updateSalesData(data) {
    document.getElementById('salesTotal').textContent = data.total;
    document.getElementById('salesRange').textContent = data.range;
  }

  // Number formatting
  function formatNumber(num) {
    return Number(num || 0).toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
  }
});

// Initialize chart with empty series and labels
const insightChartOptions = {
  series: [],
  chart: {
    height: 350,
    type: 'line',
    stacked: false,
  },
  stroke: {
    width: [0, 2, 5],
    curve: 'smooth'
  },
  plotOptions: {
    bar: {
      columnWidth: '50%'
    }
  },
  fill: {
    opacity: [0.85, 0.25, 1],
    gradient: {
      inverseColors: false,
      shade: 'light',
      type: "vertical",
      opacityFrom: 0.85,
      opacityTo: 0.55,
      stops: [0, 100, 100, 100]
    }
  },
  labels: [],
  markers: {
    size: 0
  },
  xaxis: {
    type: 'datetime'
  },
  yaxis: {
    title: {
      text: 'Quantity',
    }
  },
  tooltip: {
    shared: true,
    intersect: false,
    y: {
      formatter: function (y) {
        if (typeof y !== "undefined") {
          return y.toFixed(0) + " units";
        }
        return y;
      }
    }
  }
};

// Create chart instance
const insightChart = new ApexCharts(document.querySelector("#insight-chart"), insightChartOptions);
insightChart.render();

// Function to fetch and update chart data for a product
function updateInsightChart(productId) {
  fetch(`/api/product-insight/${productId}/`)
    .then(response => response.json())
    .then(data => {
      insightChart.updateOptions({
        labels: data.labels,
        series: [
          {
            name: 'Product Sold',
            type: 'column',
            data: data.sold
          },
          {
            name: 'Product Volume',
            type: 'area',
            data: data.purchased
          },
          {
            name: 'Demand Forecast',
            type: 'line',
            data: data.forecast
          }
        ]
      });
    })
    .catch(error => {
      console.error(error);
    });
}

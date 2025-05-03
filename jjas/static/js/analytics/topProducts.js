
const productOptions = {
  series: [],
  chart: {
    sparkline: { enabled: false },
    type: "bar",
    width: "100%",
    height: 268,
    toolbar: {
      show: true,
      tools: { pan: false },
    },
  },
  fill: { opacity: 1 },
  plotOptions: {
    bar: {
      horizontal: true,
      columnWidth: "100%",
      borderRadiusApplication: "end",
      borderRadius: 6,
      dataLabels: { position: "top" },
    },
  },
  legend: { show: true, position: "bottom" },
  dataLabels: { enabled: false },
  tooltip: {
    shared: true,
    intersect: false,
    formatter: function (value) {
      return "₱" + value.toLocaleString();
    }
  },
  xaxis: {
    categories: [],
    labels: {
      show: true,
      style: {
        fontFamily: "Inter, sans-serif",
        cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
      },
      formatter: function(value) {
        return "₱" + value.toLocaleString();
      }
    },
    axisTicks: { show: false },
    axisBorder: { show: false },
  },
  yaxis: {
    labels: {
      show: true,
      style: {
        fontFamily: "Inter, sans-serif",
        cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
      }
    }
  },
  grid: {
    show: true,
    strokeDashArray: 4,
    padding: { left: 2, right: 2, top: -20 },
  },
};


let TopProdChart;

if (document.getElementById("products-chart") && typeof ApexCharts !== 'undefined') {
  TopProdChart = new ApexCharts(document.getElementById("products-chart"), productOptions);
  TopProdChart.render();

  fetchTopProducts('last7');
}

async function fetchTopProducts(period = 'last7') {
  try {
    const response = await fetch(`/api/top-products/?period=${period}`);
    const data = await response.json();

    if (!Array.isArray(data)) {
      console.error("API response is not an array:", data);
      return;
    }

    const categories = data.map(item => item.product__name);
    const revenueData = data.map(item => parseFloat(item.total_revenue || 0));

    const updatedOptions = {
      series: [
        {
          name: "Sales Revenue",
          color: "#31C48D",
          data: revenueData,
        }
      ],
      xaxis: {
        categories: categories
      }
    };

    TopProdChart.updateOptions(updatedOptions);
  } catch (error) {
    console.error("Failed to fetch top products data:", error);
  }
}

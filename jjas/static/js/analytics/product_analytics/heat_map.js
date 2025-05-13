let cachedRawData = []; // hold all data for reuse

async function fetchAndRenderHeatmap() {
  const res = await fetch(`/api/category-sales-heatmap/?limit=1000`);
  cachedRawData = await res.json(); // store for searching
  renderHeatmap(cachedRawData); // initial render
}

function renderHeatmap(data) {
  if (!data.length) {
    document.querySelector("#heat-map-chart").innerHTML =
      "<p class='text-center text-gray-500'>No data available.</p>";
    return;
  }

  // Get the last 12 months
  const today = new Date();
  const months = [];
  for (let i = 11; i >= 0; i--) {
    const d = new Date(today.getFullYear(), today.getMonth() - i, 1);
    months.push(d.toISOString().slice(0, 7)); // 'YYYY-MM'
  }

  // Map: category -> {month: quantity}
  const categoryMap = {};
  data.forEach(({ category_code, date, total_quantity }) => {
    const month = date.slice(0, 7);
    if (!categoryMap[category_code]) categoryMap[category_code] = {};
    categoryMap[category_code][month] = total_quantity;
  });

  // Build Apex series
  const series = Object.entries(categoryMap).map(([category, monthData]) => ({
    name: category,
    data: months.map(m => monthData[m] || 0),
  }));

  const chartOptions = {
    series: series,
    chart: {
      height: 320,
      type: 'heatmap',
      toolbar: { show: false }
    },
    xaxis: {
      type: 'category',
      categories: months,
      labels: {
        formatter: val => {
          const [year, month] = val.split("-");
          const date = new Date(year, parseInt(month) - 1);
          return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
        },
        rotate: -45,
        style: { fontSize: '10px' }
      }
    },
    dataLabels: { enabled: false },
    colors: ["#008FFB"],
  };

  const chartContainer = document.querySelector("#heat-map-chart");
  chartContainer.innerHTML = ""; // Clear old chart
  const heatMapChart = new ApexCharts(chartContainer, chartOptions);
  heatMapChart.render();
}

// Handle category search
document.addEventListener("DOMContentLoaded", () => {
  fetchAndRenderHeatmap();

  const searchInput = document.querySelector("#heat-map-search");
  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();

    if (!query) {
      renderHeatmap(cachedRawData);
    } else {
      const filtered = cachedRawData.filter(item =>
        item.category_code.toLowerCase().includes(query)
      );
      renderHeatmap(filtered);
    }
  });
});

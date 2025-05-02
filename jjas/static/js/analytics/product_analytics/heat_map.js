async function fetchAndRenderHeatmap(range = 'this_year') {
  const res = await fetch(`/api/category-sales-heatmap/?range=${range}`);
  const rawData = await res.json();

  if (!rawData.length) {
    document.querySelector("#heat-map-chart").innerHTML = "<p class='text-center text-gray-500'>No data available.</p>";
    return;
  }

  // Extract unique dates and map category data
  const dateSet = new Set();
  const categoryMap = {};

  rawData.forEach(({ category_code, date, total_quantity }) => {
    dateSet.add(date);
    if (!categoryMap[category_code]) categoryMap[category_code] = {};
    categoryMap[category_code][date] = total_quantity;
  });

  const dates = Array.from(dateSet).sort(); // sorted list of all unique dates

  // Construct data for ApexCharts
  const series = Object.entries(categoryMap).map(([category, dataMap]) => ({
    name: category,
    data: dates.map(date => dataMap[date] || 0)
  }));

  const heatMapChartOptions = {
    series: series,
    chart: {
      height: 250,
      type: 'heatmap',
      toolbar: {
        show: true,
        tools: {
          zoom: false, zoomin: false, zoomout: false, pan: false,
        },
      },
    },
    xaxis: {
      type: 'category',
      categories: dates,
      labels: {
        rotate: -45,
        style: { fontSize: '10px' }
      }
    },
    dataLabels: {
      enabled: false
    },
    colors: ["#008FFB"],
  };

  const chartContainer = document.querySelector("#heat-map-chart");
  chartContainer.innerHTML = ""; // Clear previous chart
  const heatMapChart = new ApexCharts(chartContainer, heatMapChartOptions);
  heatMapChart.render();
}

document.addEventListener("DOMContentLoaded", () => {
  const dropdownItems = document.querySelectorAll('.range-option');
  const buttonLabel = document.querySelector('#dropdownDefaultButton_heatmap');

  dropdownItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const range = item.dataset.range;
      const label = item.textContent.trim();

      // Update the dropdown button label
      buttonLabel.innerHTML = `${label}
        <svg class="w-2.5 m-2.5 ms-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
        </svg>`;

      // Re-fetch and re-render the chart
      fetchAndRenderHeatmap(range);
    });
  });
});


// Call it on load
fetchAndRenderHeatmap();

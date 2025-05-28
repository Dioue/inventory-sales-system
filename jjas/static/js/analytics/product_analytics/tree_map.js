let treeMapChart = null;
let originalTreeMapData = [];

const colors = [
  '#3B93A5', '#F7B844', '#ADD8C7', '#EC3C65', '#CDD7B6',
  '#C1F666', '#D43F97', '#1E5D8C', '#421243', '#7F94B0',
  '#EF6537', '#C0ADDB'
];

const mainTreeOptions = {
  series: [{ data: [] }],
  legend: { show: false },
  chart: {
    height: 300,
    type: 'treemap',
    toolbar: { show: false }
  },
  colors: colors,
  plotOptions: {
    treemap: {
      distributed: true,
      enableShades: true
    }
  }
};

document.addEventListener('DOMContentLoaded', function () {
  treeMapChart = new ApexCharts(document.getElementById("tree-map-chart"), mainTreeOptions);
  treeMapChart.render();

  loadTreeMap();

  const searchInput = document.getElementById('tree-map-search');
  searchInput.addEventListener('input', debounce(handleSearchInput, 300));
});

// Debounce function to avoid lag on every keystroke
function debounce(func, delay = 300) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

// Load data from API
function loadTreeMap() {
  fetch(`/api/tree-map/`)
    .then(response => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then(data => {
      originalTreeMapData = data;

      // Display top 200 initially
      updateTreeMap(data.slice(0, 200));
    })
    .catch(error => {
      console.error("Error loading chart data:", error);
    });
}

// Update the chart safely
function updateTreeMap(data) {
  window.requestAnimationFrame(() => {
    treeMapChart.updateSeries([{ data }]);
  });
}

// Handle search input
function handleSearchInput(e) {
  const keyword = e.target.value.toLowerCase().trim();

  if (!keyword) {
    updateTreeMap(originalTreeMapData.slice(0, 200));
    return;
  }

  const filteredData = originalTreeMapData
    .filter(item => item.x.toLowerCase().includes(keyword))
    .slice(0, 200); // Limit display for performance

  updateTreeMap(filteredData.length ? filteredData : [{
    x: "No matching category",
    y: 0
  }]);
}


let pieChart = null;
let originalPieChartData = [];

const colors = [
  '#3B93A5', '#F7B844', '#ADD8C7', '#EC3C65', '#CDD7B6',
  '#C1F666', '#D43F97', '#1E5D8C', '#421243', '#7F94B0',
  '#EF6537', '#C0ADDB'
];

const pieOptions = {
  series: [],
  labels: [],
  chart: {
    height: 300,
    type: 'pie',
    toolbar: { show: false }
  },
  colors: colors,
  legend: {
    show: true,
    position: 'bottom'
  },
  dataLabels: {
    enabled: true,
    formatter: function (val) {
      return val.toFixed(1) + "%";
    }
  },
  responsive: [{
    breakpoint: 480,
    options: {
      chart: { width: 200 },
      legend: { position: 'bottom' }
    }
  }]
};

document.addEventListener('DOMContentLoaded', function () {
  pieChart = new ApexCharts(document.getElementById("pie-map-chart"), pieOptions);
  pieChart.render();

  loadPieData();

  const searchInput = document.getElementById('pie-map-search');
  searchInput.addEventListener('input', debounce(handleSearchInput, 300));
});

// Fetch and prepare data
function loadPieData() {
  fetch(`/api/tree-map/`)
    .then(response => {
      if (!response.ok) throw new Error("Failed to fetch chart data.");
      return response.json();
    })
    .then(data => {
      originalPieChartData = data.map(item => ({
        label: item.x,
        data: item.y
      }));
      updatePieChart(originalPieChartData);
    })
    .catch(error => {
      console.error("Error loading pie chart data:", error);
    });
}

function updatePieChart(data) {
  const series = data.map(item => item.data);
  const labels = data.map(item => item.label);

  window.requestAnimationFrame(() => {
    pieChart.updateOptions({ series, labels });
  });
}

function handleSearchInput(e) {
  const keyword = e.target.value.toLowerCase().trim();

  if (!keyword) {
    updatePieChart(originalPieChartData);
    return;
  }

  const filtered = originalPieChartData.filter(item =>
    item.label.toLowerCase().includes(keyword)
  );

  updatePieChart(filtered.length ? filtered : [{ label: "No matching category", data: 0 }]);
}

// Debounce function
function debounce(func, delay = 300) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

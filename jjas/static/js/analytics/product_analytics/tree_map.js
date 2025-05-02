let treeMapChart = null;

const colors = [
  '#3B93A5', '#F7B844', '#ADD8C7', '#EC3C65', '#CDD7B6',
  '#C1F666', '#D43F97', '#1E5D8C', '#421243', '#7F94B0',
  '#EF6537', '#C0ADDB'
];

// Initial empty options
const mainTreeOptions = {
  series: [{ data: [] }],
  legend: { show: false },
  chart: {
    height: 250,
    type: 'treemap'
  },
  colors: colors,
  plotOptions: {
    treemap: {
      distributed: true,
      enableShades: true
    }
  }
};

// Render chart once with empty data
document.addEventListener('DOMContentLoaded', function () {
  treeMapChart = new ApexCharts(document.getElementById("tree-map-chart"), mainTreeOptions);
  treeMapChart.render();

  // Load initial data for "today"
  loadTreeMap('today');

  // Handle dropdown change
  const select = document.getElementById('range-select');
  select.addEventListener('change', (e) => {
    loadTreeMap(e.target.value);
  });
});

// Fetch and update data
function loadTreeMap(range) {
  fetch(`/api/tree-map/?range=${range}`)
    .then(response => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then(data => {
      let seriesData;

      if (!data || data.length === 0) {
        // No data — show a dummy block
        seriesData = [{
          x: `No category sale ${range === 'today' ? 'today' : `in the last ${range} days`}`,
          y: 0
        }];
      } else {
        seriesData = data;
      }

      treeMapChart.updateSeries([{ data: seriesData }]);
    })
    .catch(error => {
      console.error("Error loading chart data:", error);
    });
}


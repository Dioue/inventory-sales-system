// 1. Define chart options (initial dummy data)
const revenueOptions = {
  series: [],
  chart: {
    height: 250,
    type: "area",
    fontFamily: "Inter, sans-serif",
    dropShadow: { enabled: false },
    toolbar: { show: false },
  },
  tooltip: {
    enabled: true,
    x: { show: false },
  },
  legend: { show: true },
  fill: {
    type: "gradient",
    gradient: {
      opacityFrom: 0.55,
      opacityTo: 0,
      shade: "#1C64F2",
      gradientToColors: ["#1C64F2"],
    },
  },
  dataLabels: { enabled: false },
  stroke: { width: 6 },
  grid: {
    show: false,
    strokeDashArray: 4,
    padding: { left: 2, right: 2, top: -26 },
  },
  xaxis: { categories: [] },
  yaxis: {
    show: false,
    labels: {
      formatter: function (value) {
        return '₱ ' + value;
      },
    },
  },
};

// 2. Declare chart variable
let RevChart;

if (document.getElementById("revenue-chart") && typeof ApexCharts !== 'undefined') {
  RevChart = new ApexCharts(document.getElementById("revenue-chart"), revenueOptions);
  RevChart.render();

  // 3. Fetch initial data
  fetchRevenueData();
}

async function fetchRevenueData(period = 'last7') {
  try {
    const response = await fetch(`/api/revenue-expense/?period=${period}`);
    const data = await response.json();

    // Update chart data
    const updatedOptions = {
      xaxis: {
        categories: data.categories,
        labels: {
          formatter: function (value) {
            return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          },
        },
      },
      series: [
        {
          name: "Revenue",
          data: data.revenue,
          color: "#1A56DB"
        },
        {
          name: "Expenses",
          data: data.expenses,
          color: "#7E3BF2"
        }
      ]
    };
    RevChart.updateOptions(updatedOptions);

    // ---- DOM UPDATES ----
    // Update sales total

    // Update subtitle
    const salesRangeEl = document.getElementById("revenue-sales-range");
    if (salesRangeEl) {
      const labelMap = {
        today: "sales to revenue today",
        last7: "sales to revenue this week",
        last30: "sales to revenue this month"
      };
      salesRangeEl.textContent = labelMap[period] || "sales";
    }

  } catch (error) {
    console.error("Error fetching chart data:", error);
  }
}

// 4. Dropdown behavior
document.querySelectorAll('#lastDaysdropdown_revenue a').forEach((dropdownItem) => {
  dropdownItem.addEventListener('click', (event) => {
    event.preventDefault();
    const text = dropdownItem.textContent.trim();

    let period = 'last7';
    if (text === 'Today') period = 'today';
    else if (text === 'Last 30 days') period = 'last30';

    fetchRevenueData(period);

    // Update dropdown label
    document.getElementById('dropdownDefaultButton_revenue').innerHTML = `
      ${text}
      <svg class="w-2.5 m-2.5 ms-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"
           fill="none" viewBox="0 0 10 6">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
              stroke-width="2" d="m1 1 4 4 4-4"/>
      </svg>`;
  });
});

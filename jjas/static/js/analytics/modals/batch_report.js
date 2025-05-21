const batchReportBtn = document.querySelector('.show-batch-report');
const batchReportModal = document.querySelector('#batch-report');
const batchReportHide = document.querySelector('#batch-report-hide');
const printBtn = document.querySelector('#batch-report-submit');
let populatedBatch = null;

batchReportBtn.addEventListener('click', async () => {

    const handleModalHide = () => {
        new Modal(batchReportModal, { backdrop: 'static' }).hide();
        batchReportHide.removeEventListener('click', handleModalHide);
    };
    batchReportHide.addEventListener('click', handleModalHide, { once: true });

    await populateBatchReport();
    generateChart();
    if(populatedBatch){
        new Modal(batchReportModal, { backdrop: 'static' }).show();
    }
});

printBtn.addEventListener('click', () => {
    window.print()

});

const batch_getMonthYear = () => {
    const date = new Date();
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
};

const populateBatchReport = async () => {
  try {
    const res = await fetch('/api/batch-report/');
    const data = await res.json();
    const report = data.last30Days;

    
    const title = document.querySelector('#batch-report-title');
    title.textContent = `📦 Batch Procurement Report – ${batch_getMonthYear()}`;

    // Format helpers
    const peso = (num) => `₱${parseFloat(num).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`;
    const number = (num) => parseInt(num).toLocaleString();

    // === Update Summary ===
    const summaryContainer = document.querySelector('#batch-report-content .grid');
    summaryContainer.innerHTML = `
      <div><span class="font-medium">Total Batches:</span> ${number(report.batch_total)}</div>
      <div><span class="font-medium">Items Received:</span> ${number(report.item_received)}</div>
      <div><span class="font-medium">Total Cost:</span> ${peso(report.total_cost)}</div>
      <div><span class="font-medium">Avg. Cost per Item:</span> ${peso(report.average_cost_per_item)}</div>
    `;

    // === Update Category Breakdown ===
    const table = document.querySelector('#batch-category-table');
      table.innerHTML = ''; // Clear old content

      const maxItems = 20;
      const cols = 5;
      const items = report.category.slice(0, maxItems);
      const rows = Math.ceil(items.length / cols);

      for (let r = 0; r < rows; r++) {
        const row = document.createElement('tr');
        for (let c = 0; c < cols; c++) {
          const i = r * cols + c;
          const cell = document.createElement('td');
          cell.className = 'p-1 align-top';

          if (i < items.length) {
            const item = items[i];
            cell.innerHTML = `🗂 <strong>${item.name}</strong> – ${peso(item.amount)}`;
          } else {
            cell.innerHTML = ''; // empty cell if no more items
          }

          row.appendChild(cell);
        }
        table.appendChild(row);
      }

    populatedBatch = true;
  } catch (error) {
    console.error("Failed to populate batch report data:", error);
  }
};


const generateChart = () => {
    fetch('/api/volume-stats/')
  .then(res => res.json())
  .then(data => {
    // Prepare data
    batchData = {
      last30Days: {
        total: formatNumber(data.last30Days.batch_total),
        range: "Batch Volume",
      },
    };

    batchChartData = {
      last30Days: {
        series: [{ name: 'Batch', data: data.last30Days.batch_data }],
        xaxis: { categories: data.last30Days.dates },
      },
    };

    const batchOptions = {
      chart: {
        type: 'area',
        height: 150,
        toolbar: {
          show: true,
          tools: {
            pan: false,
            zoomin: false,
            zoomout: false,
            zoom: false
          },
        },
      },
      stroke: {
          curve: 'straight'
        },
      dataLabels: { enabled: false },
      series: batchChartData.last30Days.series,
      xaxis: {
        type: 'datetime',
        categories: batchChartData.last30Days.xaxis.categories,
        labels: {
          formatter: function (value) {
            return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          },
        },
      },
    };

    const batchReportChart = new ApexCharts(document.getElementById("batch-report-chart"), batchOptions);
    batchReportChart.render();

  })
  .catch(error => console.error('Error fetching batch report data:', error));
}


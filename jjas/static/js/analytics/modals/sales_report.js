const salesReportBtn = document.querySelector('.show-sales-report');
const salesReportModal = document.querySelector('#sales-report');
const salesReportHide = document.querySelector('#sales-report-hide');
let populatedSales = null;
let salesReportChart; 

salesReportBtn.addEventListener('click', async () => {
    await loadSalesReport();
    const handleModalHide = () => {
        new Modal(salesReportModal, { backdrop: 'static' }).hide();
        salesReportHide.removeEventListener('click', handleModalHide);
    };
    salesReportHide.addEventListener('click', handleModalHide, { once: true });
    salesChartReport();
    if(populatedSales){
        new Modal(salesReportModal, { backdrop: 'static' }).show();
    }
});


async function loadSalesReport() {
    try {
        const response = await fetch('/api/sales-report/');
        const data = await response.json();

        // Set Report Month
        document.querySelector('#sales-report-month').textContent = `📊 Monthly Sales Report – ${data.report_month}`;

        // Sales Summary
        document.querySelector('#sr-total-sales strong').textContent = `₱${data.sales_summary.total_sales.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.querySelector('#sr-number-of-sales strong').textContent = data.sales_summary.number_of_sales;
        document.querySelector('#sr-average-sale strong').textContent = `₱${data.sales_summary.average_sale_value.toLocaleString(undefined, {minimumFractionDigits: 2})}`;

        // Top-Selling Products
        const topProductsBody = document.querySelector('#sr-top-products-body');
        topProductsBody.innerHTML = '';
        data.top_selling_products.forEach(item => {
            topProductsBody.innerHTML += `
                <tr class="border-t dark:border-gray-700">
                    <td class="px-4 py-2">${item.product}</td>
                    <td class="px-4 py-2">${item.quantity_sold}</td>
                    <td class="px-4 py-2">₱${item.revenue.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                </tr>
            `;
        });

        const table = document.querySelector('#sr-category-sales-table');
        table.innerHTML = ''; // Clear previous rows

        const maxItems = 20;
        const cols = 4; // You specified 4 columns
        const items = data.sales_by_category.slice(0, maxItems);
        const rows = Math.ceil(items.length / cols);

        for (let r = 0; r < rows; r++) {
        const row = document.createElement('tr');
        for (let c = 0; c < cols; c++) {
            const i = r * cols + c;
            const cell = document.createElement('td');
            cell.className = 'p-1 align-top text-sm';

            if (i < items.length) {
            const item = items[i];
            cell.innerHTML = `<strong>${item.category}</strong> – ₱${item.sales.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
            } else {
            cell.innerHTML = '';
            }

            row.appendChild(cell);
        }
        table.appendChild(row);
        }

        // Inventory Movement
        const inventoryList = document.querySelector('#sr-inventory-movement-list');
        inventoryList.innerHTML = `
            <li>⚡ Fast-Moving: <strong>${data.inventory_movement.fast_moving.join(', ')}</strong></li>
            <li>🐢 Slow-Moving: <strong>${data.inventory_movement.slow_moving.join(', ')}</strong></li>
            <li>⚠️ Low Stock: <strong>${data.inventory_movement.low_stock_alerts.map(p => `${p.name} (Qty: ${p.quantity})`).join(', ')}</strong></li>
        `;

        // Top Clients
        const topClientsList = document.querySelector('#sr-top-clients-list');
        topClientsList.innerHTML = '';
        data.top_clients.forEach(client => {
            topClientsList.innerHTML += `<li>${client.name} – ₱${client.sales.toLocaleString(undefined, {minimumFractionDigits: 2})}</li>`;
        });

        // Delivery Insights
        const deliveryList = document.querySelector('#sr-delivery-insights-list');
        deliveryList.innerHTML = `
            <li>📦 Total Deliveries: ${data.delivery_insights.total_deliveries}</li>
            <li>✅ On-Time: ${data.delivery_insights.on_time}</li>
            <li>⏰ Late: ${data.delivery_insights.late}</li>
        `;
        populatedSales = true;
    } catch (error) {
        console.error("Failed to load sales report:", error);
    }
}

document.querySelector('#sr-submit').addEventListener('click', () => {
    const reportContent = document.querySelector('#sr-print-area');
    if (!reportContent) return;

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const doc = printWindow.document;

    // Build <html>
    const html = doc.createElement('html');
    const head = doc.createElement('head');
    const body = doc.createElement('body');

    // <title>
    const title = doc.createElement('title');
    title.textContent = 'Sales Report';

    // Tailwind CSS link
    const tailwind = doc.createElement('link');
    tailwind.rel = 'stylesheet';
    tailwind.href = 'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css';

    // Custom print styles
    const style = doc.createElement('style');
    style.textContent = `
        @media print {
            body {
                font-family: sans-serif;
                background: white;
                padding: 1rem;
            }
            .apexcharts-toolbar {
                display: none !important;
            }
            .apexcharts-canvas,
            svg {
                width: 100% !important;
                height: auto !important;
            }
        }
    `;

    head.appendChild(title);
    head.appendChild(tailwind);
    head.appendChild(style);

    const contentClone = reportContent.cloneNode(true);
    body.appendChild(contentClone);

    const script = doc.createElement('script');
    script.textContent = `
        window.onload = function () {
            try {
                if (window.salesReportChart) {
                    window.salesReportChart.resize();
                }
            } catch (e) {}
            window.print();
            window.onafterprint = () => window.close();
        };
    `;

    body.appendChild(script);
    html.appendChild(head);
    html.appendChild(body);
    doc.replaceChild(html, doc.documentElement);
});



const salesChartReport = () => {
    fetch('/api/volume-stats/')
    .then(res => res.json())
    .then(data => {
        // ... existing data preparation

        const salesOptions = {
            chart: {
                type: 'area',
                height: 200,
                toolbar: {
                    show: false // Hide toolbar completely for both screen and print
                },
            },
            dataLabels: { enabled: false },
            series: salesChartData.last30Days.series,
            xaxis: {
                type: 'datetime',
                categories: salesChartData.last30Days.xaxis.categories,
                labels: {
                    formatter: function (value) {
                        return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                    },
                },
            },
        };

        salesReportChart = new ApexCharts(document.getElementById("sr-chart"), salesOptions);
        salesReportChart.render();
    })
    .catch(error => console.error('Error fetching sales data:', error));
}
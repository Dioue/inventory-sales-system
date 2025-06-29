function printCurrentTable() {
    // Get the table container
    const tableContainer = document.querySelector('.relative.overflow-x-auto');

    if (!tableContainer) {
        alert("No table found to print.");
        return;
    }

    // Open a new print window
    const printWindow = window.open('', '', 'width=900,height=650');
    const styles = `
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .no-print { display: none !important; }
        </style>
    `;


    printWindow.document.write(`
        <html>
            <head>
                <title>Print Table</title>
                ${styles}
            </head>
            <body>
                <h2>Table Report</h2>
                ${tableContainer.innerHTML}
            </body>
        </html>
    `);
    printWindow.document.close();

    // Wait for content to load before printing
}
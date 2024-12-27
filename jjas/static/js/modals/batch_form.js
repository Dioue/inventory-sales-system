document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('table-search');
    const dropdown = document.getElementById('product-dropdown');
    const noData = document.getElementById('no-data');
    const tableBody = document.getElementById('batch_table_body');

    /**
     * Filter dropdown items based on search input.
     */
    searchInput.addEventListener('input', () => {
        const filter = searchInput.value.toLowerCase();
        const items = dropdown.getElementsByClassName('product-item');
        let hasMatch = false;

        if (filter.length > 0) {
            dropdown.classList.remove('hidden');

            Array.from(items).forEach(item => {
                const text = item.textContent || item.innerText;
                if (text.toLowerCase().includes(filter)) {
                    item.style.display = "";
                    hasMatch = true;
                } else {
                    item.style.display = "none";
                }
            });

            noData.classList.toggle('hidden', hasMatch);
        } else {
            resetDropdown(items);
        }
    });

    /**
     * Add product to table on dropdown item click.
     */
    dropdown.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('product-item')) {
            const productText = event.target.textContent.trim();
            const [productCode, productName] = productText.split(' - ');
            const productCost = event.target.dataset.sellingPrice; // Get the selling price from the data attribute
    
            if (!isProductInTable(productName)) {
                addProductRow(productName, productCost); // Pass the selling price to addProductRow
                resetDropdown();
            } else {
                alert('Product already added to the table.');
            }
        }
    });
    

    /**
     * Remove product row from table.
     */
    tableBody.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('remove-row')) {
            event.preventDefault();
            event.target.closest('tr').remove();
        }
    });

    /**
     * Reset dropdown visibility and item display states.
     */
    function resetDropdown(items) {
        dropdown.classList.add('hidden');
        Array.from(items || dropdown.getElementsByClassName('product-item')).forEach(item => {
            item.style.display = "";
        });
        noData.classList.add('hidden');
    }

    /**
     * Check if a product is already in the table.
     */
    function isProductInTable(productName) {
        return Array.from(tableBody.querySelectorAll('tr')).some(row => {
            return row.querySelector('.product-name')?.textContent === productName;
        });
    }

    /**
     * Add a new product row to the table.
     */
    function addProductRow(productName, productCost) {
        const newRow = document.createElement('tr');
        newRow.className = "bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600";
        newRow.innerHTML = `
            <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white product-name">${productName}</td>
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <button class="inline-flex items-center justify-center p-1 me-3 text-sm font-medium h-6 w-6 text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                        <span class="sr-only">Decrease Quantity</span>
                        <svg class="w-3 h-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h16"/>
                        </svg>
                    </button>
                    <input type="number" class="bg-gray-50 w-14 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block px-2.5 py-1 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" value="1" min="1">
                    <button class="inline-flex items-center justify-center h-6 w-6 p-1 ms-3 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                        <span class="sr-only">Increase Quantity</span>
                        <svg class="w-3 h-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 1v16M1 9h16"/>
                        </svg>
                    </button>
                </div>
            </td>
            <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white">$${productCost}</td>
            <td class="px-6 py-4">
                <a href="#" class="font-medium text-red-600 dark:text-red-500 hover:underline remove-row">Remove</a>
            </td>
        `;
        tableBody.appendChild(newRow);
    }    
});

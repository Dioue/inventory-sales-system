

/* Batch Data fetching in API for search input */
// Fetch product data from the API once
const fetchBatchData = async () => {
    try {
        const response = await fetch(`/api/products/`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);

        const products = await response.json();
        return products;
    } catch (error) {
        console.error('Error fetching products:', error);
        return [];
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    const searchInput = document.getElementById('table-search');
    const dropdown = document.getElementById('product-dropdown');
    const noData = document.getElementById('no-data');
    const tableBody = document.getElementById('batch_table_body');
    let allProducts = [];

    // Fetch all products once when the page loads
    allProducts = await fetchBatchData();

    // Search functionality
    searchInput.addEventListener('input', () => {
        const filter = searchInput.value.toLowerCase();

        if (filter.length > 0) {
            const filteredProducts = allProducts.filter(product => {
                const regex = new RegExp(`^${filter}`, 'i');
                return regex.test(product.code) || regex.test(product.name);
            });
            populateDropdown(filteredProducts);
        } else {
            resetDropdown();
        }
    });

    function populateDropdown(products) {
        // Remove dynamically added items but keep the "no-data" element
        const dynamicItems = dropdown.querySelectorAll('li:not(#no-data)');
        dynamicItems.forEach(item => item.remove());
    
        if (products.length > 0) {
            products.forEach(product => {
                const item = document.createElement('li');
                item.className = 'product-item px-4 py-2 text-sm cursor-pointer hover:text-gray-800 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white';
                item.dataset.id = product.id;
                item.textContent = `${product.code} - ${product.name}`;
                dropdown.appendChild(item);
            });
            dropdown.classList.remove('hidden');
            noData.classList.add('hidden');
        } else {
            dropdown.classList.remove('hidden'); // Show the dropdown to display "no-data"
            noData.classList.remove('hidden');  // Make sure "no-data" is visible
        }
    }
    
    // Reset dropdown when no matches are found or input is cleared
    function resetDropdown() {
        const dynamicItems = dropdown.querySelectorAll('li:not(#no-data)');
        dynamicItems.forEach(item => item.remove());
        dropdown.classList.add('hidden');
        noData.classList.remove('hidden');
    }

    // Add product to table on dropdown item click
    dropdown.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('product-item')) {
            const productText = event.target.textContent.trim();
            const [productCode, productName] = productText.split(' - ');
            const productId = event.target.dataset.id;

            if (!isProductInTable(productName)) {
                addProductRow(productName, productId);
                resetDropdown();
            } else {
                alert('Product already added to the table.');
            }
        }
    });

    // Remove product row from the table
    tableBody.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('remove-row')) {
            event.preventDefault();
            event.target.closest('tr').remove();
        }
    });

    // Check if a product is already in the table
    function isProductInTable(productName) {
        return Array.from(tableBody.querySelectorAll('tr')).some(row => {
            return row.querySelector('.product-name')?.textContent === productName;
        });
    }

    // Add a new product row to the table
    function addProductRow(productName, productId) {
        const newRow = document.createElement('tr');
        newRow.className = "bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600";
        newRow.innerHTML = `
            <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white product-name">${productName}</td>
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <button onclick="batch_quantity_decrease(${productId})" class="inline-flex items-center justify-center p-1 me-3 text-sm font-medium h-6 w-6 text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                        <span class="sr-only">Decrease Quantity</span>
                        <svg class="w-3 h-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h16"/>
                        </svg>
                    </button>
                    <input id="quantity-${productId}" type="number" min=0 class="bg-gray-50 w-14 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block px-2.5 py-1 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" value="1" min="1">
                    <button onclick="batch_quantity_increase(${productId})" class="inline-flex items-center justify-center h-6 w-6 p-1 ms-3 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                        <span class="sr-only">Increase Quantity</span>
                        <svg class="w-3 h-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 1v16M1 9h16"/>
                        </svg>
                    </button>
                </div>
            </td>
            <td class="font-semibold text-gray-900 dark:text-white">
                <div class="relative">
                    <div class="absolute inset-y-0 start-0 flex items-center ps-3.5 pointer-events-none">
                        <span>₱</span>
                    </div>
                    <input id="cost-${productId}" type="number" step="0.01" min="0" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-10/12 ps-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="00.00">
                </div>
            </td>
            <td class="px-6 py-4">
                <a href="#" class="font-medium text-red-600 dark:text-red-500 hover:underline remove-row">Remove</a>
            </td>
        `;
        tableBody.appendChild(newRow);
    }
});

/**
 * Decrease batch quantity
 */
const batch_quantity_decrease = (item_id) => {
    const quantityInput = document.getElementById(`quantity-${item_id}`);
    let currentValue = parseInt(quantityInput.value, 10);
    if (currentValue > 1) {
        quantityInput.value = currentValue - 1;
    }
};

/**
 * Increase batch quantity
 */
const batch_quantity_increase = (item_id) => {
    const quantityInput = document.getElementById(`quantity-${item_id}`);
    let currentValue = parseInt(quantityInput.value, 10);
    quantityInput.value = currentValue + 1;
};

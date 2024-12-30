

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

    searchInput.addEventListener('click', async () => {
        // Fetch all products once when the page loads
        allProducts = await fetchBatchData();
    });

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
                item.dataset.unit = product.unit?.name ?? 'No unit';
                item.dataset.cost = product.cost_price;
                item.dataset.selling = product.selling_price;
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
        searchInput.value = '';
    }

    // Add product to table on dropdown item click
    dropdown.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('product-item')) {
            const productText = event.target.textContent.trim();
            const [productCode, name] = productText.split(' - ');
            const id = event.target.dataset.id;
            const unit = event.target.dataset.unit;
            const cost = event.target.dataset.cost;
            const selling = event.target.dataset.selling;

            if (!isProductInTable(name)) {
                const newRow = document.createElement('tr');
                newRow.className = "bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600";
                newRow.innerHTML = `
                    <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white product-name">${name}</td>
                    <td class="px-0 py-4">
                        <div class="relative flex items-center w-10/12 max-w-[11rem]">
                            <button type="button" id="decrement-quantity" onclick="batch_function_decrease('quantity', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-s-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                                <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h16"/>
                                </svg>
                            </button>
                            <input type="text" onblur="setToOneOnExit(this)"  id="quantity-${id}" oninput="sanitizeToOne(this)" aria-describedby="helper-text-explanation" class="bg-gray-50 border-x-0 border-gray-300 h-11 font-medium text-center text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-8/12 pb-6 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="" value="1" min="0" max="9999" required />
                            <div class="absolute bottom-1 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 flex items-center text-xs text-gray-600 space-x-1 rtl:space-x-reverse">
                                <span>${unit}</span>
                            </div>
                            <button type="button" id="increment-quantity" onclick="batch_function_increase('quantity', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-e-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                                <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
                                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 1v16M1 9h16"/>
                                </svg>
                            </button>
                        </div>
                    </td>
                    <td class="px-0 py-4">
                        <div class="relative flex items-center w-10/12 max-w-[11rem]">
                            <button type="button" id="decrement-defective" onclick="batch_function_decrease('defective', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-s-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                                <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h16"/>
                                </svg>
                            </button>
                            <input type="text" id="defective-${id}" onblur="setToOneOnExit(this)" oninput="sanitizeToZero(this)" aria-describedby="helper-text-explanation" class="bg-gray-50 border-x-0 border-gray-300 h-11 font-medium text-center text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-8/12 pb-6 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="" value="0" min="0" max="999" required />
                            <div class="absolute bottom-1 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 flex items-center text-xs text-gray-600 space-x-1 rtl:space-x-reverse">
                                <span>${unit}</span>
                            </div>
                            <button type="button" id="increment-defective" onclick="batch_function_increase('defective', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-e-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                                <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
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
                            <input 
                                id="cost-${id}" 
                                type="number" 
                                step="0.01" 
                                min="0"
                                oninput="updateTotal(${id})"
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-10/12 ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" 
                                placeholder="0.00" 
                                style="text-align: right;" 
                                onkeydown="if(event.key === 'e' || event.key === 'E' || event.key === '+' || event.key === '-') event.preventDefault();"
                            >
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <p 
                            id="total-${id}" 
                            class="font-bold text-gray-700 overflow-hidden whitespace-nowrap text-ellipsis" 
                            style="width: 6rem; height: 1.5rem; display: inline-block; text-align: right;"
                        > ₱ 0.00
                        </p>
                    </td>

                    <td class="px-6 py-4">
                        <a href="#" class="font-medium text-red-600 dark:text-red-500 hover:underline remove-row">Remove</a>
                    </td>
                `;
                tableBody.appendChild(newRow);
                resetDropdown();
            } else {
                alert('Product already added to the table.');
                resetDropdown();
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

});


// This update the field id='quantity-${id}' to match [quantity] x [cost]
function updateTotal(id) {

    const quantityInput = document.getElementById(`quantity-${id}`);
    const costInput = document.getElementById(`cost-${id}`);
    const totalElement = document.getElementById(`total-${id}`);
    
    const quantity = parseFloat(quantityInput.value) || 0;
    const cost = parseFloat(costInput.value) || 0;

    const total = quantity * cost;
    // Format the total with commas
    const formattedTotal = total.toLocaleString('en-US', { style: 'currency', currency: 'PHP' });

    // Update the total element
    totalElement.textContent = formattedTotal;
}


/* Sanitation of inputs because the UI used is a type='text'. Like why????  */
function sanitizeToOne(inputElement) {  

    if (isNaN(inputElement.value)) {
        inputElement.value = 1;
    } else {
        inputElement.value = inputElement.value.replace(/\s/g, '');
    } 
}

const setToOneOnExit = (inputElement) => {
    if (inputElement.value.trim() === '') {
        inputElement.value = 1;  // Set to 1 if invalid
    }
}

function sanitizeToZero(inputElement) {  
    const quantityInput = document.getElementById(`quantity-${inputElement.id.split('-')[1]}`);
    const parseValue = parseInt(inputElement.value) || 0;
    const qP = parseInt(quantityInput.value) || 0;

    if (isNaN(inputElement.value)) {
        inputElement.value = 0;
    } else if (parseValue > qP) {
        inputElement.value = quantityInput.value
    } else {
        inputElement.value = inputElement.value.replace(/\s/g, '');
    }
}

/**
 * Decrease batch quantity
 */
const batch_function_decrease = (item_name, item_id) => {
    const input = document.getElementById(`${item_name}-${item_id}`);
    let currentValue = parseInt(input.value, 10);
    
    
    if (item_name === 'quantity' && currentValue > 1) {
        input.value = currentValue - 1;
    } else if (currentValue > 0 && item_name ==='defective') {
        input.value = currentValue - 1;
    }

    updateTotal(item_id) 
};

/**
 * Increase batch quantity
 */
const batch_function_increase = (item_name, item_id) => {
    
    const input = document.getElementById(`${item_name}-${item_id}`);
    let currentValue = parseInt(input.value, 10);
    

    if(item_name === 'defective'){
        const quantityInput = document.getElementById(`quantity-${item_id}`)
        const defectiveInput = document.getElementById(`defective-${item_id}`)
        const val = parseInt(defectiveInput.value, 10);
        const maxVal = parseInt(quantityInput.value, 10);
        input.value = (val < maxVal) ? currentValue + 1 : currentValue;
    } else {
        input.value = currentValue + 1;
    }   

    updateTotal(item_id) 
};

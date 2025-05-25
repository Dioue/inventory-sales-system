
// show a view quackity quack
const view = document.querySelectorAll('.batch_view');
const edit = document.querySelectorAll('.batch_edit');
const _modalView = document.getElementById('default_item_view');
const _modalEdit = document.getElementById('batch_update');
const _modalViewHideBtn = document.querySelector('.default_item_view_hide');
const _modalEditHideBtn = document.getElementById('batch_update_hide_btn');
const _noData = document.getElementById('no-data');
const _dropdown = document.getElementById('product-dropdown-update');
const _searchInput = document.getElementById('table-search-update');
const _tableBody = document.getElementById('batch-tbody-update');
const _setStatic = {"backdrop": "static"}
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
let _table_filled = false;
let _products = null;
let update_units = [];
let update_category = [];
let gp = 0;


// Function to fetch product details
async function fetchBatchDetails(id) {
    try {
        const response = await fetch(`/api/batch-orders/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch batch (ID: ${id}): ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching batch:', error);
        throw error;
    }
}

const fetchProductData = async () => {
    try {
        const response = await fetch(`/api/products/`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);

        const prod = await response.json();
        _products = prod;
        return prod;
    } catch (error) {
        console.error('Error fetching products:', error);
        return [];
    }
};

const fetchUnitsUpdate = async () => {
    try {
        const response = await fetch(`/api/units/`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        update_units = await response.json();
    } catch (error) {
        console.error('Error fetching units:', error);
    }
};

const fetchCategoryUpdate = async () => {
    try {
        const response = await fetch(`/api/category/`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        update_category = await response.json();
    } catch (error) {
        console.error('Error fetching category:', error);
    }
};


// Start of function handling
async function handleViewClick(event) {
    const id = event.currentTarget.dataset.id;
    if (id) {
        try {
            const batch = await fetchBatchDetails(id);
            const header_id = document.querySelector('.default_view_header_id');
            const batch_id = document.getElementById('view_batch_id');
            const grand_total = document.getElementById('view_gt');
            const supplier_name = document.getElementById('view_sn');
            const purchase_date = document.getElementById('view_pd');

            // Update modal fields
            header_id.innerText = `BN-${batch.id}`;
            batch_id.innerText = batch.id;
            grand_total.innerText = parseFloat(batch.grand_total).toLocaleString('en-US', { style: 'currency', currency: 'PHP' });
            supplier_name.innerText = batch.supplier;
            purchase_date.innerText = batch.purchase_date;

            let batch_table_instance = null;

            const tableEl = document.querySelector("#batch-view-table");

            if (typeof simpleDatatables !== 'undefined' &&
                typeof simpleDatatables.DataTable !== 'undefined' &&
                tableEl) {

                // Initialize the table
                batch_table_instance = new simpleDatatables.DataTable(tableEl, {
                    searchable: true,
                    sortable: true,
                    perPage: 10,
                    perPageSelect: [5, 10],
                });

                // Use a short delay to wait for internal setup
                setTimeout(async () => {
                    if (batch_table_instance && batch && Array.isArray(batch.items)) {
                        const rows = [];

                        const fetchPromises = batch.items.map(item => fetchFilteredProductsReadOnly(item.product));
                        try {
                            const productDataList = await Promise.all(fetchPromises); 
                            batch.items.forEach((item, index) => {
                                const productData = productDataList[index];
                                rows.push([
                                    item.product,
                                    productData[index].name,
                                    item.cost_price,
                                    item.quantity,
                                    item.defective
                                ]);
                            });

                            batch_table_instance.insert({ data: rows });
                        } catch (err) {
                            console.error("Error fetching product data or inserting rows:", err);
                        }
                    }
                }, 50); // 10–50ms is usually enough
            }

            new Modal(_modalView, _setStatic).show();

        } catch (error) {
            console.error('Error handling view click:', error);
        }
    }
}

function handleModalHide() {
    if (dataTableInstance) {
        dataTableInstance.destroy();
        dataTableInstance = null;
    }
}

view.forEach(el => el.addEventListener('click', handleViewClick));
_modalViewHideBtn.addEventListener('click', () => {
    new Modal(_modalView, _setStatic).hide();
    handleModalHide();
});



// Function to handle edit button click and update request to server
async function handleEditClick(event) {
    const id = event.currentTarget.dataset.id;
    if (id) {
        try {
            const batch = await fetchBatchDetails(id);
            document.getElementById('supplier-input-update').value = batch.supplier;
            const dateParts = batch.purchase_date.split('-');
            const formattedDate = `${dateParts[1]}/${dateParts[2]}/${dateParts[0]}`;
            document.getElementById('purchase-date-update').value = formattedDate;
            document.querySelector('.bu-header-id').innerText = `BN-${batch.id}`;

            // update the search again omg its so repetitive ive done this on batch create
            _searchInput.addEventListener('click', async () => {
                _products = await fetchProductData();
                
            })

            _searchInput.addEventListener('input', () => {
                const filter = _searchInput.value.toLowerCase();
        
                if (filter.length > 0) {
                    const filtered_Products = _products.filter(product => {
                        const regex = new RegExp(`^${filter}`, 'i');
                        return regex.test(product.code) || regex.test(product.name);
                    });
                    _populate_Dropdown(filtered_Products);
                } else {
                    reset_Dropdown();
                }
            });

            if (batch.items.length > 0) {
                _tableBody.innerHTML = '';
                batch.items.forEach(async item => {
                    const _p = await fetchFilteredProductsReadOnly(item.product)
                    const nRow = createRow(_p[0].id, _p[0].name, _p[0].unit.name, item.cost_price, _p[0].critical_level, item.quantity, item.defective)
                    _tableBody.appendChild(nRow);
                    updateTotalBU(_p[0].id);
                })
                updateGrandBU();
                _table_filled = true;
            }

            /* For batch confirmation */
            document.getElementById('batch-update-btn').addEventListener('click', function (event) {
                const modalElement = document.getElementById('confirm_batch_update_popup');
                new Modal(modalElement).show();

            });
            
            document.getElementById('confirm_batch_update_submit').addEventListener('click', batchPut);


            document.querySelectorAll('.confirm-batch-update-hide').forEach((element) => {
            element.addEventListener('click', function () {
                const modalElement = document.getElementById('confirm_batch_update_popup');
                new Modal(modalElement).hide(); // Close the modal
            });
            });

            if(_table_filled){
                new Modal(_modalEdit, _setStatic).show();
            }
        } catch (error) {
            console.error('Error handling view click:', error);
        }
    }
}


edit.forEach(el => el.addEventListener('click', handleEditClick));
_modalEditHideBtn.addEventListener('click', () => {
    new Modal(_modalEdit, _setStatic).hide();
});


// Throw away functions that are copied from the batch create because I am tired of looking at them




document.addEventListener('DOMContentLoaded', async () => {
    await fetchProductData();
    await fetchUnitsUpdate();
    await fetchCategoryUpdate();
})

function _populate_Dropdown(_products) {
    // Remove dynamically added items but keep the "no-data" element
    const dynamicItems = _dropdown.querySelectorAll('li:not(#no-data)');
    dynamicItems.forEach(item => item.remove());

    if (_products.length > 0) {
        _products.forEach(async product => {

            let unitName = 'No unit'; 
            if (product.unit) {
                const unit = update_units.find(unit => unit.id === product.unit);

                if (unit) {
                    unitName = unit.name;
                }
            }

            if (product.category) {
                const category = update_category.find(cat => cat.id === product.category);

                if (category) {
                    product_category = category.code;
                }
            }



            const item = document.createElement('li');
            item.className = 'product-item px-4 py-2 text-sm cursor-pointer hover:text-gray-800 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white';
            item.dataset.id = product.id;
            item.dataset.cost = product.cost_price;
            item.dataset.selling = product.selling_price;
            item.dataset.crit = product.critical_level
            item.dataset.name = product.name;
            item.textContent = `(${product_category}-${product.code}) ${product.name}`;
            item.dataset.unit = unitName;

            _dropdown.appendChild(item);
        });
        _dropdown.classList.remove('hidden');
        _noData.classList.add('hidden');
    } else {
        _dropdown.classList.remove('hidden'); // Show the _dropdown to display "no-data"
        _noData.classList.remove('hidden');  // Make sure "no-data" is visible
    }
}

// Reset _dropdown when no matches are found or input is cleared
function reset_Dropdown() {
    const dynamicItems = _dropdown.querySelectorAll('li:not(#no-data)');
    dynamicItems.forEach(item => item.remove());
    _dropdown.classList.add('hidden');
    _noData.classList.remove('hidden');
    _searchInput.value = '';
}

// Add product to table on _dropdown item click
_dropdown.addEventListener('click', (event) => {
    if (event.target && event.target.classList.contains('product-item')) {
        const productText = event.target.textContent.trim();
        const name = event.target.dataset.name;
        const id = event.target.dataset.id;
        const unit = event.target.dataset.unit;
        const cost = event.target.dataset.cost;
        const crit = event.target.dataset.crit;

        if (!isProductInTable(name)) {
            let nRow = createRow(id, name, unit, cost, crit);
            _tableBody.appendChild(nRow);
            updateGrandBU();
            reset_Dropdown();
            
        } else {
            alert('Product already added to the table.');
            reset_Dropdown();
        }
    }
});

// Remove product row from the table
_tableBody.addEventListener('click', (event) => {
    if (event.target && event.target.classList.contains('remove-row')) {
        event.preventDefault();
        event.target.closest('tr').remove();
    }

    updateGrandBU();
});

// Check if a product is already in the table
function isProductInTable(productName) {
    return Array.from(_tableBody.querySelectorAll('tr')).some(row => {
        return row.querySelector('.product-name')?.textContent === productName;
    });
}


function createRow(id, name, unit, cost, crit, quantity = 1, defective_count = 0, grand_total){
    const newRow = document.createElement('tr');
            newRow.className = "bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600";
            newRow.dataset.id = id;
            newRow.dataset.crit = crit;
            newRow.innerHTML = `
                <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white product-name">${name}</td>
                <td class="px-0 py-4">
                    <div class="relative flex items-center w-10/12 max-w-[11rem]">
                        <button type="button" id="decrement-quantity" onclick="batch_function_decrease_update('quantity', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-s-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                            <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h16"/>
                            </svg>
                        </button>
                        <input type="text" onblur="setToOneOnExitUpdate(this)"  id="quantity-${id}" oninput="sanitizeToOneUpdate(this)" aria-describedby="helper-text-explanation" class="bg-gray-50 border-x-0 border-gray-300 h-11 font-medium text-center text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-8/12 pb-6 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="" value="${quantity}" min="0" max="9999" required />
                        <div class="absolute bottom-1 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 flex items-center text-xs text-gray-600 space-x-1 rtl:space-x-reverse">
                            <span>${unit}</span>
                        </div>
                        <button type="button" id="increment-quantity" onclick="batch_function_increase_update('quantity', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-e-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                            <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
                                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 1v16M1 9h16"/>
                            </svg>
                        </button>
                    </div>
                </td>
                <td class="px-0 py-4">
                    <div class="relative flex items-center w-10/12 max-w-[11rem]">
                        <button type="button" id="decrement-defective" onclick="batch_function_decrease_update('defective', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-s-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                            <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h16"/>
                            </svg>
                        </button>
                        <input type="text" id="defective-${id}" onblur="setToOneOnExitUpdate(this)" oninput="sanitizeToZeroUpdate(this)" aria-describedby="helper-text-explanation" class="bg-gray-50 border-x-0 border-gray-300 h-11 font-medium text-center text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-8/12 pb-6 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="" value="${defective_count}" min="0" max="999" required />
                        <div class="absolute bottom-1 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 flex items-center text-xs text-gray-600 space-x-1 rtl:space-x-reverse">
                            <span>${unit}</span>
                        </div>
                        <button type="button" id="increment-defective" onclick="batch_function_increase_update('defective', ${id})" class="bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-e-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
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
                            oninput="updateTotalBU(${id})"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-10/12 ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" 
                            placeholder="0.00" 
                            style="text-align: right;" 
                            onkeydown="if(event.key === 'e' || event.key === 'E' || event.key === '+' || event.key === '-') event.preventDefault();"
                            value = "${cost}"
                        >
                    </div>
                </td>
                <td class="px-6 py-4">
                    <p 
                        id="total-${id}" 
                        class="total-price font-bold text-gray-700 overflow-hidden whitespace-nowrap text-ellipsis" 
                        style="width: 6rem; height: 1.5rem; display: inline-block; text-align: right;"
                    > ₱ ${cost}
                    </p>
                </td>

                <td class="px-6 py-4">
                    <a href="#" class="font-medium text-red-600 dark:text-red-500 hover:underline remove-row">Remove</a>
                </td>
            `;

    return newRow;
}

// This update the field id='quantity-${id}' to match [quantity] x [cost]
function updateTotalBU(id) {

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

    updateGrandBU()
}

function updateGrandBU() {
    const grand_price = document.querySelector('.batch-grand-price');
    const total_price = document.querySelectorAll('.total-price');

    // Update total grand price
    let grand_total = 0;
    total_price.forEach(el => {
        const price_text = el.innerText.replace(/[^\d.]/g, ''); // Remove non-numeric characters except '.'
        const price = parseFloat(price_text) || 0;
        grand_total += price;
    });

    const formattedGrand = grand_total.toLocaleString('en-US', { style: 'currency', currency: 'PHP' });
    grand_price.innerText = formattedGrand;
    gp = grand_total
}


/* Sanitation of inputs because the UI used is a type='text'. Like why????  */
function sanitizeToOneUpdate(inputElement) {  
    const value = inputElement.value;

    if (isNaN(value)) {
        inputElement.value = 1;
    } else {
        inputElement.value = value.includes('.') 
            ? value.replace(/\./g, '')
            : value.replace(/\s/g, ''); 
    }

    const id = inputElement.id.split('-')[1];
    updateTotalBU(id);
}


const setToOneOnExitUpdate = (inputElement) => {
    if (inputElement.value.trim() === '' || inputElement.value.includes('.')) {
        inputElement.value = 1;  // Set to 1 if invalid
    }
    const id = inputElement.id.split('-')[1]
    updateTotalBU(id)
}

function sanitizeToZeroUpdate(inputElement) {  
    const quantityInput = document.getElementById(`quantity-${inputElement.id.split('-')[1]}`);
    const parseValue = parseInt(inputElement.value) || 0;
    const qP = parseInt(quantityInput.value) || 0;

    if (isNaN(inputElement.value) || inputElement.value.includes('.')) {
        inputElement.value = 0;
    } else if (parseValue > qP) {
        inputElement.value = quantityInput.value
    } else {
        inputElement.value = value.includes('.') 
            ? value.replace(/\./g, '')
            : value.replace(/\s/g, ''); 
    }

    const id = inputElement.id.split('-')[1]
    updateTotalBU(id)
}

/**
 * Decrease batch quantity
 */
const batch_function_decrease_update = (item_name, item_id) => {
    const input = document.getElementById(`${item_name}-${item_id}`);
    let currentValue = parseInt(input.value, 10);
    
    
    if (item_name === 'quantity' && currentValue > 1) {
        input.value = currentValue - 1;
    } else if (currentValue > 0 && item_name ==='defective') {
        input.value = currentValue - 1;
    }

    updateTotalBU(item_id) 
};

/**
 * Increase batch quantity
 */
const batch_function_increase_update = (item_name, item_id) => {
    
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

    updateTotalBU(item_id) 
};


async function batchPut() {
    try {
        // Gather data from the form
        const supplier = document.getElementById('supplier-input-update').value.trim();
        const purchaseDate = document.getElementById('purchase-date-update').value.trim(); // MM/DD/YYYY format
        
        const items = [];
        const rows = document.querySelectorAll('#batch-tbody-update tr');

        rows.forEach(row => {
            const productId = row.dataset.id;
            const quantity = row.querySelector('[id^="quantity-"]').value;
            const costPrice = row.querySelector('[id^="cost-"]').value;
            const defective = row.querySelector('[id^="defective-"]').value;
            items.push({
                product: productId,
                quantity: parseInt(quantity) || 0,
                defective: parseInt(defective) || 0,
                cost_price: parseFloat(costPrice) || 0,
            });
        });

        const batchId = document.querySelector('.bu-header-id').innerText.replace('BN-', '').trim();

        // Format purchase date to ISO (YYYY-MM-DD)
        const [month, day, year] = purchaseDate.split('/');
        const formattedDate = `${year}-${month}-${day}`;

        // Construct the payload
        const payload = {
            supplier,
            purchase_date: formattedDate,
            grand_total: gp,
            items,
        };


        // Send the PUT request
        const response = await fetch(`/api/batch-orders/${batchId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`Failed to update batch: ${response.status}`);
        }

        const data = await response.json();

        // Optionally, reload or refresh the UI after success
        alert('Batch updated successfully!');
        location.reload();
    } catch (error) {
        console.error('Error updating batch:', error);
        alert('Failed to update batch. Please try again.');
    }
}
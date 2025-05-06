const createBtn = document.querySelector('.item-create-btn');
const updateBtn = document.querySelectorAll('.sales-update-btn');
const salesForm = document.querySelector('#sales-form');
const salesFormHide = document.querySelector('.sales-form-hide');
const formControl = document.querySelector('#sales-form-control');
const formSearch = document.querySelector('#sales-form-search');
const formSearchDropdown = document.querySelector('#sales-form-dropdown');
const formTbody = document.querySelector('#sales-form-tbody');
const formNoData = document.getElementById('no-data');
const submitBtn = document.querySelector('#sales-form-submit');
const confirmModal = document.querySelector('#confirm-sales');
const confirmBtn = document.querySelector('#confirm-submit');
const confirmHide = document.querySelectorAll('.confirm-sales-hide');
const modalOptions = {'backdrop': 'static'};
const salesFormGrand = document.querySelector('.sales-form-grand-total');
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
let allProducts = null;
let allUnits = null;
let allCategory = null;

// Global form control
const formId = document.querySelector('#sales-form-id');
const formClient = document.querySelector("#sales-form-client");
const formIssued = document.querySelector('#sales-form-issued');
const formNet = document.querySelector("#sales-form-net");
const formPayment = document.querySelector('#sales-form-status');
const formAdressOne = document.querySelector('#sales-form-address-line-1');
const formAdressTwo = document.querySelector('#sales-form-address-line-2');
const formCity = document.querySelector('#sales-form-city');
const formProvince = document.querySelector('#sales-form-province');
const formZip = document.querySelector('#sales-form-zip');

// API Fetch
const fetchSales = async (id = null) => {
    try {
        const url = id === null ? `/api/sales-records/` : `/api/sales-records/${id}/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch sales: ${response.statusText}`);
        }
        return await response.json();
        
    } catch (error) {
        console.error('Error fetching sales records:', error);
        throw error;
    }
}

const fetchProducts = async (id = null) => {
    try {
        const url = id === null ? `/api/products/` : `/api/products/${id}/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch product: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching product: `, error);
        throw error;
    }
}

const fetchUnits = async () => {
    try {
        const response = await fetch(`/api/units/`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching units:', error);
    }

};

const fetchCategory = async () => {
    try {
        const response = await fetch(`/api/category/`);
        if (!response.ok) throw new Error(`Error: ${response.statusText}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching category:', error);
    }
};


// On DOM Load Calls
document.addEventListener('DOMContentLoaded', async () =>{
    allUnits = await fetchUnits();
    allCategory = await fetchCategory();

    formSearch.addEventListener('click', async () => {
        allProducts = await fetchProducts();
    })
})


// DOM controllers
createBtn.addEventListener('click', async () => {
    const sales = await fetchSales();
    const maxId = Math.max(...sales.map(sale => sale.id), 0) + 1;

    // form data injection to DOM
    formId.innerText = `SN-${(maxId).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;

    // reset form
    hitTheQuan()

    const handleSubmit = async () => {
        new Modal(confirmModal, modalOptions).show();
        const handleConfirmClick = async () => {
            await salesAPI('POST');
            new Modal(confirmModal, modalOptions).hide();
        };
    
        confirmBtn.addEventListener('click', handleConfirmClick, { once: true });
    
        confirmHide.forEach(el => {
            el.addEventListener('click', () => {
                confirmBtn.removeEventListener('click', handleConfirmClick);
                new Modal(confirmModal, modalOptions).hide();
            }, {once: true})
        })
    };

    const handleModalHide = () => {
        new Modal(salesForm, modalOptions).hide();
        salesFormHide.removeEventListener('click', handleModalHide);
    };

    submitBtn.addEventListener('click', handleSubmit);
    salesFormHide.addEventListener('click', handleModalHide, { once: true });
    new Modal(salesForm, modalOptions).show();
})

let isSubmitHandlerAttached = false;

updateBtn.forEach(el => {
    el.addEventListener('click', async (event) => {
        try {
            const allProducts = await fetchProducts();
            const sale = await fetchSales(event.target.dataset.id);
            const dateParts = sale.date_issued.split('-');
            const formattedDate = `${dateParts[1]}/${dateParts[2]}/${dateParts[0]}`;
            

            // reset the form
            hitTheQuan();
            formId.innerText = `SN-${sale.id}`;
            formClient.value = sale.client.name;
            formIssued.value = formattedDate;
            formNet.value = sale.net_day;
            formPayment.value = sale.status;
            formAdressOne.value = sale.client.address_line_1;
            formAdressTwo.value = sale.client.address_line_2;
            formCity.value = sale.client.city;
            formProvince.value = sale.client.province;
            formZip.value = sale.client.zip_code;

            sale.items.forEach(item => {
                const prod = allProducts.find(prod => prod.id === item.product)
                appendToTBody(item.product, item.product_name, prod.cost_price, prod.selling_price, item.quantity, item.surcharge)
            })

            const handleSubmit = async () => {
                new Modal(confirmModal, modalOptions).show();
                const handleConfirmClick = async () => {
                    await salesAPI('PUT', sale.id);
                    new Modal(confirmModal, modalOptions).hide();
                };
    
                confirmBtn.addEventListener('click', handleConfirmClick, { once: true });
    
                confirmHide.forEach(el => {
                    el.addEventListener('click', () => {
                        confirmBtn.removeEventListener('click', handleConfirmClick);
                        new Modal(confirmModal, modalOptions).hide();
                    }, { once: true });
                });
            };
            
            const handleModalHide = () => {
                new Modal(salesForm, modalOptions).hide();
                if (isSubmitHandlerAttached) {
                    submitBtn.removeEventListener('click', handleSubmit);
                    isSubmitHandlerAttached = false;
                }
                salesFormHide.removeEventListener('click', handleModalHide);
            };
    
            if (!isSubmitHandlerAttached) {
                submitBtn.addEventListener('click', handleSubmit);
                isSubmitHandlerAttached = true;
            }

            salesFormHide.addEventListener('click', handleModalHide, { once: true });
            new Modal(salesForm, modalOptions).show();
        } catch (error) {
            console.error('Error fetching sale data:', error);
        }
    });
});


//Form reset
const hitTheQuan = () => {
    formClient.value = '';
    formIssued.value = '';
    formNet.value = '';
    formPayment.value = '';
    formAdressOne.value = '';
    formAdressTwo.value = '';
    formCity.value = '';
    formProvince.value = ''; 
    formZip.value ='';
    formTbody.innerHTML = '';
}

// Search controllers
formSearch.addEventListener('input', async() => {
    const filter = formSearch.value.toLowerCase();
    if (filter.length > 0) {
        const filteredProducts = allProducts.filter(product => {
            const regex = new RegExp(`^${filter}`, 'i');
            return regex.test(product.code) || regex.test(product.name);
        });
        populateDropdown(filteredProducts);
    } else {
        resetDropdown();
    }
})

// form search reset
function resetDropdown() {
    const dynamicItems = formSearchDropdown.querySelectorAll('li:not(#no-data)');
    dynamicItems.forEach(item => item.remove());
    formSearchDropdown.classList.add('hidden');
    formNoData.classList.remove('hidden');
    formSearch.value = '';
}

// Dropdown populator for form search
function populateDropdown(products) {
    // Remove dynamically added items but keep the "no-data" element
    const dynamicItems = formSearchDropdown.querySelectorAll('li:not(#no-data)');
    dynamicItems.forEach(item => item.remove());
    if (products.length > 0) {
        products.forEach(async product => {
            let unitName = 'No unit'; 
            if (product.unit) {
                const unit = allUnits.find(unit => unit.id === product.unit);
                if (unit) {
                    unitName = unit.name;
                }
            }
            if (product.category) {
                const category = allCategory.find(cat => cat.id === product.category);
                if (category) {
                    product_category = category.code;
                }
            }
            const item = document.createElement('li');
            item.className = 'sales-form-items px-4 py-2 text-sm cursor-pointer hover:text-gray-800 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white';
            item.dataset.id = product.id;
            item.dataset.cost = product.cost_price;
            item.dataset.selling = product.selling_price;
            item.dataset.crit = product.critical_level;
            item.dataset.quantity = product.quantity;
            item.dataset.name = product.name;
            item.dataset.unit = unitName;
            item.textContent = `(${product_category}-${product.code}) ${product.name}`;
            if(product.quantity === 0) {
                item.className = 'sales-form-items px-4 py-2 text-sm cursor-pointer  bg-gray-100 text-gray-600   hover:text-gray-800 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white disabled';
                item.textContent = `(${product_category}-${product.code}) ${product.name} (No stock)`;
            }
            formSearchDropdown.appendChild(item);
        });
        formSearchDropdown.classList.remove('hidden');
        formNoData.classList.add('hidden');
    } else {
        formSearchDropdown.classList.remove('hidden'); // Show the dropdown to display "no-data"
        formNoData.classList.remove('hidden');  // Make sure "no-data" is visible
    }
}

// The populator
formSearchDropdown.addEventListener('click', (event) =>{
    if (event.target && event.target.classList.contains('sales-form-items')) {
        if(event.target.dataset.quantity > 0){
            const prodId = event.target.dataset.id;
            const prodName = event.target.dataset.name;
            const prodCost = event.target.dataset.cost;
            const prodSelling = event.target.dataset.selling;
            const prodQuantity = event.target.dataset.quantity;
            if(!isProductInTable(prodName)){
                appendToTBody(prodId, prodName, prodCost, prodSelling, prodQuantity);
            }
        }
    }
})

// Remove product row from the table
formTbody.addEventListener('click', (event) => {
    if (event.target && event.target.classList.contains('remove-row')) {
        event.preventDefault();
        event.target.closest('tr').remove();
    }

    updateGrand();
});

// Check if a product is already in the table
function isProductInTable(productName) {
    return Array.from(formTbody.querySelectorAll('tr')).some(row => {
        return row.querySelector('.product-name')?.textContent === productName;
    });
}

const appendToTBody = (prodId, prodName, prodCost, prodSelling, prodQuantity, surcharge="0.00") => {
    const newRow = document.createElement('tr');
    newRow.dataset.id = prodId;
    newRow.className = "bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600";
    newRow.innerHTML = `
        <td class="product-name-${prodId} px-6 py-4 font-semibold text-gray-900 dark:text-white">${prodName}</td>
        <td class="product-cost-${prodId} px-6 py-4 font-semibold text-gray-900 dark:text-white">₱${prodCost}</td>
        <td class="product-selling-${prodId} px-6 py-4 font-semibold text-gray-900 dark:text-white">₱${prodSelling}
        </td>
        <td class="pl-6 py-4">
            <div class="relative flex items-start w-10/12 max-w-[11rem]">
                <button type="button" id="decrement-quantity" onclick="btn_decrease('quantity', ${prodId})" class=" dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-s-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                    <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 2">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h16"/>
                    </svg>
                </button>
                <input type="text" onblur="setToOneOnExit(this, ${prodQuantity})"  id="quantity-${prodId}" oninput="sanitizeToOne(this, ${prodQuantity})" aria-describedby="helper-text-explanation" class=" border-x-0 border-gray-300 h-11 font-medium text-center text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-8/12 pb-6 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="" value="${prodQuantity}" min="0" max="9999" required />
                <div class="absolute bottom-1 start-1/2 -translate-x-1/2 rtl:translate-x-1/2 flex items-center text-xs text-gray-600 space-x-1 rtl:space-x-reverse">
                    <span>Max: ${prodQuantity}</span>
                </div>
                <button type="button" id="increment-quantity" onclick="btn_increase('quantity', ${prodId}, ${prodQuantity})" class=" dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 hover:bg-gray-200 border border-gray-300 rounded-e-lg p-3 h-11 focus:ring-gray-100 dark:focus:ring-gray-700 focus:ring-2 focus:outline-none">
                    <svg class="w-3 h-3 text-gray-900 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 18">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 1v16M1 9h16"/>
                    </svg>
                </button>
            </div>
        </td>
        <td class="pl-6 py-4 font-semibold text-gray-900 max-w-6 dark:text-white">
            <div class="relative">
                <input 
                    id="surcharge-${prodId}" 
                    type="number" 
                    step="0.01" 
                    min="0"
                    max="100"
                    onblur="sanitizeToZero(this, 100)"
                    oninput="sanitizeToZero(this, 100)"
                    class="border border-gray-300 text-sm rounded-lg  w-8/12" 
                    placeholder="0.00" 
                    style="text-align: right;" 
                    onkeydown="if(event.key === 'e' || event.key === 'E' || event.key === '+' || event.key === '-') event.preventDefault();"
                    value = ${surcharge}
                >
            </div>
        </td>
        <td id="item-total-${prodId}" class="px-6 py-4 font-semibold text-gray-900 dark:text-white product-name">
        </td>
        <td class="px-6 py-4">
            <a href="#" class="font-medium text-red-600 dark:text-red-500 hover:underline remove-row">Remove</a>
        </td>
        
    `;
    formTbody.appendChild(newRow);
    updateTotal(prodId);
    resetDropdown();
    
}

function sanitizeToOne(inputElement, item_quantity) {  
    const value = inputElement.value;
    const maxVal = parseInt(item_quantity, 10) || 0;
    if (isNaN(value)) {
        inputElement.value = 1;
    } else if (value > maxVal){
        inputElement.value = maxVal
    } else {
        inputElement.value = value.includes('.') 
            ? value.replace(/\./g, '')
            : value.replace(/\s/g, ''); 
    }

    const id = inputElement.id.split('-')[1];
    updateTotal(id);
}

function sanitizeToZero(inputElement, maxVal) {  
    const value = inputElement.value;
    if (value !== '0' && value !== '0.' && /^0+\d/.test(value)) {
        value = value.replace(/^0+/, '');
    }
    if (isNaN(value)) {
        inputElement.value = 0;
    } else if (value > maxVal){
        inputElement.value = maxVal
    } else if (value === ''){
        inputElement.value = 0.00;
    }

    const id = inputElement.id.split('-')[1];
    updateTotal(id);
}


const setToOneOnExit = (inputElement, item_quantity) => {
    const maxVal = parseInt(item_quantity, 10) || 0;
    if (inputElement.value.trim() === '' || inputElement.value.includes('.')) {
        inputElement.value = 1;  // Set to 1 if invalid
    } else if (value > maxVal){
        inputElement.value = maxVal
    }

    const id = inputElement.id.split('-')[1];
    updateTotal(id);
}


/**
 * Decrease batch quantity
 */
const btn_decrease = (item_name, item_id) => {
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
const btn_increase = (item_name, item_id, item_max) => {
    const input = document.getElementById(`${item_name}-${item_id}`);
    let currentValue = parseInt(input.value, 10) || 0;
    let maxVal = parseInt(item_max, 10);

    if (currentValue < maxVal) {
        input.value = currentValue + 1;
    }

    updateTotal(item_id)
};


const updateTotal = (id) => {
    const totalElement = document.querySelector(`#item-total-${id}`); // Get the DOM element
    const quantityVal = parseInt(document.querySelector(`#quantity-${id}`).value, 10);
    const surchargeVal = parseFloat(document.querySelector(`#surcharge-${id}`).value, 10);
    const sellingVal = parseFloat(document.querySelector(`.product-selling-${id}`).innerText.replace(/[^\d.]/g, ''), 10);

    let total = quantityVal * (sellingVal + (sellingVal * (surchargeVal / 100)));
    total = parseFloat(total).toLocaleString('en-US', { style: 'currency', currency: 'PHP' });
    totalElement.innerText = `${total}`

    updateGrand();
};

const updateGrand = () => {
    const totalPrices = document.querySelectorAll('[id^="item-total-"')
    let total = 0;
    totalPrices.forEach(el => {
        total += parseFloat(el.innerText.replace(/[^\d.]/g, ''), 10)
    })

    total = parseFloat(total).toLocaleString('en-US', { style: 'currency', currency: 'PHP' });
    salesFormGrand.innerText = `${total}`
}


const salesAPI = async (mode, id = null) => {
    // Check if the values are correct first
    if (!formClient.value){
        generic_alert("Client name cannot be empty.")
        return;
    } else if (!formIssued.value && formatDate(formIssued.value)){
        generic_alert("Please provide a valid date.")
        return;
    } else if (formNet.value === '' || formPayment.value === ''){
        generic_alert("Please select a net day.")
        return;
    } else if (!formAdressOne.value || !formCity.value || !formProvince.value || !formZip.value) {
        generic_alert("Please fill out all required address fields")
        return;
    } else if (formTbody.rows.length === 0) { // Check if tbody has rows
        generic_alert("Please add at least one product to the sales record.");
        return;
    }

    // Determine the API endpoint based on mode
    const url = mode === 'POST' ? '/api/sales-records/' : `/api/sales-records/${id}/`;
    const method = mode === 'POST' ? 'POST' : 'PUT';
    console.log('API URL:', url);
    console.log('API Method:', method);

    // Extract the grand total value
    const grand_total = parseFloat(salesFormGrand.innerText.replace(/[^\d.]/g, ''), 10);

    // Prepare items array from table rows
    const items = [];
    const rows = document.querySelectorAll('#sales-form-tbody tr');
    rows.forEach(row => {
        const productId = row.dataset.id;
        const quantity = row.querySelector('[id^="quantity-"]').value;
        const surcharge = row.querySelector('[id^="surcharge-"]').value;
        const total = row.querySelector('[id^="item-total-"]').innerText.replace(/[^\d.]/g, '');

        items.push({
            product: productId,
            quantity: parseInt(quantity) || 0,
            surcharge: parseFloat(surcharge) || 0,
            total: parseFloat(total) || 0,
        });
    });


    // Construct the payload
    const payload = {
        client: {
            name: formClient.value.trim(),
            address_line_1: formAdressOne.value.trim(),
            address_line_2: formAdressTwo.value.trim(),
            city: formCity.value.trim(),
            province: formProvince.value.trim(),
            zip_code: formZip.value.trim(),
        },
        date_issued: formatDate(formIssued.value.trim()),
        net_day: parseInt(formNet.value) || 30,
        status: formPayment.value === "true",
        total: grand_total,
        items,
    };

    // Log the payload for debugging
    console.log('Payload:', payload);

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(payload),
        });
    
        if (response.ok) {
            const data = await response.json();
            console.log('API Response Submitted:', data);
            generic_alert('Sales record successfully saved.', reload = true);
        } else {
            let errorText = '';
            try {
                const error = await response.json();
                errorText = JSON.stringify(error);
            } catch {
                errorText = await response.json();
            }
            console.error('API Error:', errorText);
            generic_alert('Error saving sales record. Please check your input.');
        }        
    
    } catch (error) {
        console.error(error);
        generic_alert('An unexpected error occurred.');
    }
    
};

// Date formatter
function formatDate(date) {
    const dateObj = new Date(date);
    if (isNaN(dateObj)) return null;

    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
}

const createBtn = document.querySelector('.item-create-btn');
const salesForm = document.querySelector('#sales-form');
const salesFormHide = document.querySelector('.sales-form-hide');
const formControl = document.querySelector('#sales-form-control');
const modalOptions = {'backdrop': 'static'};

// Global form control
const formId = document.querySelector('#sales-form-id');


// API Fetch
const fetchSales = async () => {
    try {
        const response = await fetch(`/api/sales-records/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch sales: ${response.statusText}`);
        }
        return await response.json();
        
    } catch (error) {
        console.error('Error fetching sales records:', error);
        throw error;
    }
}

const fetchProducts = async () => {
    try {
        const response = await fetch(`/api/products/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch product: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching product: `, error);
        throw error;
    }
}



// DOM controllers
createBtn.addEventListener('click', async () => {

    const sales = await fetchSales();
    const maxId = Math.max(...sales.map(sale => sale.id), 0) + 1;

    // form data injection to DOM
    formId.innerText = `SN-${(maxId).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;

    const handleModalHide = () => {
        new Modal(salesForm, modalOptions).hide();
        salesFormHide.removeEventListener('click', handleModalHide);
    };
    salesFormHide.addEventListener('click', handleModalHide, { once: true });
    new Modal(salesForm, modalOptions).show();
})
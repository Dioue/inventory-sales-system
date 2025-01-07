
const createBtn = document.querySelector('.item-create-btn');
const deliveryForm = document.querySelector('#delivery-form');
const deliveryFormHide = document.querySelector('.delivery-form-hide');
const formControl = document.querySelector('#delivery-form-control');
const deliveryDateInput = document.getElementById('delivery-form-issued');
const dateClaimedInput = document.getElementById('delivery-form-claimed');
const saleSelected = document.querySelector('#delivery-form-sale');
const saleIssued = document.querySelector('#delivery-form-issued');
const saleClaimed = document.querySelector('#delivery-form-claimed');
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value; 
const submitBtn = document.getElementById('delivery-form-submit');
const confirmModal = document.getElementById('confirm-delivery');
const confirmBtn = document.getElementById('confirm-submit');
const confirmHide = document.querySelectorAll('.confirm-delivery-hide');
const modalOptions = {'backdrop': 'static'};
let allSales = null;
let sale_issued = null;
// Global form control
const formId = document.querySelector('#delivery-form-id');


// API Fetch
const fetchdelivery = async () => {
    try {
        const response = await fetch(`/api/delivery/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch delivery: ${response.statusText}`);
        }
        return await response.json();
        
    } catch (error) {
        console.error('Error fetching delivery:', error);
        throw error;
    }
}


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

// DOM controllers
createBtn.addEventListener('click', async () => {

    const delivery = await fetchdelivery();
    const maxId = Math.max(...delivery.map(d => d.id), 0) + 1;

    // form data injection to DOM
    formId.innerText = `DN-${(maxId).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;

    saleSelected.addEventListener("change", async function (event) {
        try {
            const sale = await fetchSales(event.target.value);
            if (sale) {
                saleSelected.dataset.id = sale.id;
                deliveryDateInput.removeAttribute('disabled');
                dateClaimedInput.removeAttribute('disabled');
                const dateParts = sale.date_issued.split('-');
                const formattedDate = `${dateParts[1]}-${dateParts[2]}-${dateParts[0]}`;
                deliveryDateInput.value = formattedDate
                dateClaimedInput.value = ''
                sale_issued = new Date(sale.date_issued);
            } else {
                deliveryDateInput.addAttribute('disabled');
                dateClaimedInput.addAttribute('disabled');
            }
        } catch (error) {
            console.error("Error fetching sale:", error);
        }
    });

    const handleSubmit = async () => {
        new Modal(confirmModal, modalOptions).show();
        const handleConfirmClick = async () => {
            await deliveryAPI('POST');
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

    submitBtn.addEventListener('click', handleSubmit);
    const handleModalHide = () => {
        new Modal(deliveryForm, modalOptions).hide();
        sale_issued = null;
        submitBtn.removeEventListener('click', handleSubmit);
        deliveryFormHide.removeEventListener('click', handleModalHide);
    };
    deliveryFormHide.addEventListener('click', handleModalHide, { once: true });
    new Modal(deliveryForm, modalOptions).show();
})


const deliveryAPI = async (method, id = null) => {
    const deliveryDate = new Date(deliveryDateInput.value);
    const dateClaimed = new Date(dateClaimedInput.value);

    // Check if `date_claimed` is valid and >= `delivery_date`
    if (isNaN(deliveryDate) || isNaN(dateClaimed)) {
        generic_alert('Error: Invalid date format.');
        return;
    }

    if (dateClaimed < deliveryDate) {
        generic_alert('Error: Date claimed cannot be earlier than the delivery date.');
        return;
    } else if (deliveryDate >= sale_issued) {
        generic_alert('Error: delivery date cannot be earlier than the sale issued date.');
        return;
    }

    const payload = {
        sale: saleSelected.dataset.id,
        delivery_date: deliveryDate.toISOString().split('T')[0],
        date_claimed: dateClaimed.toISOString().split('T')[0],
    };

    console.log(payload);

    const url = id ? `/api/delivery/${id}/` : '/api/delivery/';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(payload),
        });
        const responseBody = await response.json();
        if (!response.ok) {
            console.log('Error Response:', responseBody);
            throw new Error(`Failed to ${method === 'POST' ? 'create' : 'update'} delivery.`);
        }
        
        generic_alert(`Delivery ${method === 'POST' ? 'created' : 'updated'} successfully.`, reload = true);
    } catch (error) {
        generic_alert(`Error: ${error.message}`);
    }
};

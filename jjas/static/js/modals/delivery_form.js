
const createBtn = document.querySelector('.item-create-btn');
const editBtn = document.querySelectorAll('.delivery-edit-btn');
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
let allDel = null;
// Global form control
const formId = document.querySelector('#delivery-form-id');


// API Fetch
const fetchDelivery = async (id = null) => {
    try {
        const url = id === null ? `/api/delivery/` : `/api/delivery/${id}/`;
        const response = await fetch(url);
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

// Load on DOM
document.addEventListener('DOMContentLoaded', async () => {
    allDel = await fetchDelivery();
})

// DOM controllers
createBtn.addEventListener('click', async () => {
    familyGuy();
    const delivery = await fetchDelivery();
    const maxId = Math.max(...delivery.map(d => d.id), 0) + 1;

    // form data injection to DOM
    formId.innerText = `DN-${(maxId).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;

    saleSelected.addEventListener("change", async function (event) {
        try {
            const sale = await fetchSales(event.target.value);
            if (sale) {
                saleSelected.dataset.id = sale.id;
                deliveryDateInput.disabled = false;
                dateClaimedInput.disabled = false;
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


editBtn.forEach(el => {
    el.addEventListener('click', async (event) => {

        const del = await fetchDelivery(event.target.dataset.id);
        if (del) {
            formId.innerText = `DN-${del.id}`
            familyGuy();
            saleSelected.value = del.sale;
            saleSelected.disabled = true; 
            deliveryDateInput.disabled = false;
            dateClaimedInput.disabled = false;
            const dateParts = del.delivery_date.split('-');
            const claimedParts = del.date_claimed.split('-');
            const formattedDate = `${dateParts[1]}-${dateParts[2]}-${dateParts[0]}`;
            const formattedClaimed = `${claimedParts[1]}-${claimedParts[2]}-${claimedParts[0]}`;
            deliveryDateInput.value = formattedDate;
            dateClaimedInput.value = formattedClaimed;
        }


        const handleSubmit = async () => {
            new Modal(confirmModal, modalOptions).show();
            const handleConfirmClick = async () => {
                await deliveryAPI('PUT', del.id);
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
            familyGuy();
            submitBtn.removeEventListener('click', handleSubmit);
            deliveryFormHide.removeEventListener('click', handleModalHide);
        };
        deliveryFormHide.addEventListener('click', handleModalHide, { once: true });
        new Modal(deliveryForm, modalOptions).show();

    })
})

const familyGuy = () => {
    deliveryDateInput.disabled = true
    dateClaimedInput.disabled = true;
    deliveryDateInput.value = '';
    dateClaimedInput.value = '';
    saleSelected.value = ''
    saleSelected.disabled = false;
}


const deliveryAPI = async (method, id = null) => {
    const deliveryDate = new Date(deliveryDateInput.value);
    const dateClaimed = new Date(dateClaimedInput.value);
    const issued_sale = new Date(sale_issued);

    // Check if `date_claimed` is valid and >= `delivery_date`
    if (isNaN(deliveryDate) || isNaN(dateClaimed)) {
        generic_alert('Error: Invalid date format.');
        return;
    }

    if (dateClaimed < deliveryDate) {
        generic_alert('Error: Date claimed cannot be earlier than the delivery date.');
        return;
    } else if (deliveryDate < issued_sale && deliveryDate.toDateString() !== issued_sale.toDateString()) {
        generic_alert('Error: delivery date cannot be earlier than the sale issued date.');
        return;
    } else if (method === 'POST') {
        const existingDel = allDel.find(del => del.sale == saleSelected.dataset.id) // if exists
        console.log(allDel)
        if(existingDel) {
            generic_alert('Error: Cannot save another delivery with the same sale number.');
            return;
        }
    }   

    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    const payload = {
        sale: saleSelected.dataset.id,
        delivery_date: formatDate(deliveryDate),
        date_claimed: formatDate(dateClaimed),
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
            throw new Error(`Failed to ${method === 'POST' ? 'create' : 'update'} delivery.`, reload=true);
        }
        
        generic_alert(`Delivery ${method === 'POST' ? 'created' : 'updated'} successfully.`);
    } catch (error) {
        generic_alert(`Error: ${error.message}`);
    }
};

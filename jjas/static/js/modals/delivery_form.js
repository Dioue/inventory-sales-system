const createBtn = document.querySelector('.item-create-btn');
const deliveryForm = document.querySelector('#delivery-form');
const deliveryFormHide = document.querySelector('.delivery-form-hide');
const formControl = document.querySelector('#delivery-form-control');
const deliveryDateInput = document.getElementById('delivery-form-issued');
const dateClaimedInput = document.getElementById('delivery-form-claimed');
const modalOptions = {'backdrop': 'static'};

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


// DOM controllers
createBtn.addEventListener('click', async () => {

    const delivery = await fetchdelivery();
    const maxId = Math.max(...delivery.map(d => d.id), 0) + 1;

    // form data injection to DOM
    formId.innerText = `DN-${(maxId).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;

    const handleModalHide = () => {
        new Modal(deliveryForm, modalOptions).hide();
        deliveryFormHide.removeEventListener('click', handleModalHide);
    };
    deliveryFormHide.addEventListener('click', handleModalHide, { once: true });
    new Modal(deliveryForm, modalOptions).show();
})


// Delivery date and claimed behaviour
console.log(deliveryDateInput, dateClaimedInput)
deliveryDateInput.addEventListener('change', () => {
    const deliveryDateValue = deliveryDateInput.value;
    if (deliveryDateValue) {
        // Set the minimum date for Date Claimed
        const minDate = new Date(deliveryDateValue);
        const minDateString = minDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD
        dateClaimedInput.setAttribute('datepicker-min-date', minDateString);
    } else {
        dateClaimedInput.removeAttribute('datepicker-min-date');
        dateClaimedInput.value = '';
    }
});

// API Fetch

const fetchSupplier = async (params = null) => {
    try {
        const response = (params == null) ?  await fetch(`/api/supplier/`): await fetch(`/api/supplier/${params}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch supplier (ID: ${params}): ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching supplier:', error);
        throw error;
    }
}

// Load necessary API on DOM load
document.addEventListener('DOMContentLoaded', async () => {
})

// DOM Access
const modalCreateBtn = document.querySelector('.item-create-btn');
const modalUpdateBtns = document.querySelectorAll('.supplier-edit');
const supplierForm = document.getElementById('supplier-form');
const submitBtn = document.getElementById('supplier-submit');
const confirmModal = document.getElementById('confirm-supplier');
const confirmBtn = document.getElementById('confirm-submit');
const confirmHide = document.querySelectorAll('.confirm-supplier-hide');
const modalHideBtn = document.querySelector('.supplier-form-hide-btn');
const modalOptions = {'backdrop': 'static'};
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value; 

// Supplier form fields
const formId = document.querySelector('.supplier-form-id');
const supplierName = document.getElementById('supplier-name');
const supplierAddress = document.getElementById('supplier-address');
const supplierContact = document.getElementById('supplier-contact');
const supplierEmail = document.getElementById('supplier-email');
const supplierWebsite = document.getElementById('supplier-website');

modalCreateBtn.addEventListener('click', async () => {
    const maxId = await fetchSupplier('max_id')
    formId.innerText = `SPN-${(maxId.max_id).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;

    supplierName.value = '';
    supplierAddress.value = '';
    supplierContact.value = '';
    supplierEmail.value = '';
    supplierWebsite.value = '';
    

    const handleSubmit = async () => {
        new Modal(confirmModal, modalOptions).show();
        const handleConfirmClick = async () => {
            await supplierAPI('POST');
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
    new Modal(supplierForm, modalOptions).show();

    const handleModalHide = () => {
        new Modal(supplierForm, modalOptions).hide();
        submitBtn.removeEventListener('click', handleSubmit);
        modalHideBtn.removeEventListener('click', handleModalHide);
    };

    modalHideBtn.addEventListener('click', handleModalHide, { once: true });
});

// Modal for Update
modalUpdateBtns.forEach(el => {
    el.addEventListener('click', async (event) => {
        const id = event.currentTarget.dataset.id;
        const supplier = await fetchSupplier(id);

        supplierName.value = '';
        supplierAddress.value = '';
        supplierContact.value = '';
        supplierEmail.value = '';
        supplierWebsite.value = '';

        formId.innerText = `SPN-${supplier.id}`;
        supplierName.value = supplier.name;
        supplierAddress.value = supplier.address;
        supplierContact.value = supplier.contact_number;
        supplierEmail.value = supplier.email;
        supplierWebsite.value = supplier.website;

        const handleSubmit = async () => {
            new Modal(confirmModal, modalOptions).show();
            const handleConfirmClick = async () => {
                await supplierAPI('PUT', id);
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
        new Modal(supplierForm,modalOptions).show();

        const handleModalHide = () => {
            new Modal(supplierForm,modalOptions).hide();
            submitBtn.removeEventListener('click', handleSubmit);
            modalHideBtn.removeEventListener('click', handleModalHide);
        };

        modalHideBtn.addEventListener('click', handleModalHide, { once: true });
    });
});

// Sanitizer to remove all input related mf that can inject code to the database (special characters and trailing whitespaces. Not including inner spaces)
function sanitizer(input) {
    return input.trim().replace(/[^a-zA-Z0-9\s-]/g, '');
}

// API for POST and PUT OMG AGAIN
const supplierAPI = async (method, id = null) => {
    const name = sanitizer(supplierName.value);
    const address = sanitizer(supplierAddress.value);
    const contact = sanitizer(supplierContact.value);
    const email = sanitizer(supplierEmail.value);
    const website = sanitizer(supplierWebsite.value);

    if (!name) {
        generic_alert('Please add a valid supplier name.');
        return;
    } 


    const payload = { 
        name: name,
        address: address,
        contact_number: contact,
        email: email,
        website: website
    };

    const url = id ? `/api/supplier/${id}/` : '/api/supplier/';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            let errorMessage = `Failed to update batch. Status: ${response.status} ${response.statusText}`;
            
            try {
                const errorBody = await response.text();  // or response.json() if you expect JSON
                errorMessage += ` | Response: ${errorBody}`;
            } catch (e) {
                errorMessage += ' | Failed to read response body.';
            }

            throw new Error(errorMessage);
        }

        generic_alert(`Supplier ${method === 'POST' ? 'created' : 'updated'} successfully.`, reload= true);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
};




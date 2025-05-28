// DOM Access
const modalCreateBtn = document.querySelector('.item-create-btn');
const modalUpdateBtns = document.querySelectorAll('.client-edit');
const clientForm = document.getElementById('client-form');
const submitBtn = document.getElementById('client-submit');
const confirmModal = document.getElementById('confirm-client');
const confirmBtn = document.getElementById('confirm-submit');
const confirmHide = document.querySelectorAll('.confirm-client-hide');
const modalHideBtn = document.querySelector('.client-form-hide-btn');
const modalOptions = {'backdrop': 'static'};
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value; 

// Client form fields
const formId = document.querySelector('.client-form-id');
const clientName = document.getElementById('client-name');
const clientAddress1 = document.getElementById('client-address-1');
const clientAddress2 = document.getElementById('client-address-2');
const clientCity = document.getElementById('client-city');
const clientProvice = document.getElementById('client-province');
const clientZip = document.getElementById('client-zip');

const fetchClient = async (params = null) => {
    try {
        const response = (params == null) ?  await fetch(`/api/client/`): await fetch(`/api/client/${params}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch client (ID: ${params}): ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching client:', error);
        throw error;
    }
}

modalCreateBtn.addEventListener('click', async () => {
    const maxId = await fetchClient('max_id')
    formId.innerText = `CLN-${(maxId.max_id).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;

    clientName.value = '';
    clientAddress1.value = '';
    clientAddress2.value = '';
    clientCity.value = '';
    clientProvice.value = '';
    clientZip.value = '';

    const handleSubmit = async () => {
        new Modal(confirmModal, modalOptions).show();
        const handleConfirmClick = async () => {
            await clientAPI('POST');
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
    new Modal(clientForm, modalOptions).show();

    const handleModalHide = () => {
        new Modal(clientForm, modalOptions).hide();
        submitBtn.removeEventListener('click', handleSubmit);
        modalHideBtn.removeEventListener('click', handleModalHide);
    };

    modalHideBtn.addEventListener('click', handleModalHide, { once: true });
});

// Modal for Update
modalUpdateBtns.forEach(el => {
    el.addEventListener('click', async (event) => {
        const id = event.currentTarget.dataset.id;
        const client = await fetchClient(id);

        formId.innerText = `CLN-${client.id}`;
        clientName.value = client.name;
        clientAddress1.value = client.address_line_1;
        clientAddress2.value = client.address_line_2;
        clientCity.value = client.city;
        clientProvice.value = client.province;
        clientZip.value = client.zip_code;

        const handleSubmit = async () => {
            new Modal(confirmModal, modalOptions).show();
            const handleConfirmClick = async () => {
                await clientAPI('PUT', id);
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
        new Modal(clientForm,modalOptions).show();

        const handleModalHide = () => {
            new Modal(clientForm,modalOptions).hide();
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
const clientAPI = async (method, id = null) => {
    const name = sanitizer(clientName.value);
    const address1 = sanitizer(clientAddress1.value);
    const address2 = sanitizer(clientAddress2.value);
    const city = sanitizer(clientCity.value);
    const province = sanitizer(clientProvice.value);
    const zip = sanitizer(clientZip.value);

    if (!name) {
        alert('Please add a valid client name.');
        return;
    } else if (!address1) {
        alert('Please add a valid address line 1.');
        return;
    } else if (!city) {
        alert('Please add a valid city.');
        return;
    } else if (!province) {
        alert('Please add a valid province.');
        return;
    } else if (!zip) {
        alert('Please add a valid zip code.');
        return;
    }

    const payload = { name: name, address_line_1: address1, address_line_2: address2, city: city, province: province, zip_code: zip };
    const url = id ? `/api/client/${id}/` : '/api/client/';

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
            let errorMessage = `Failed to update client. Status: ${response.status} ${response.statusText}`;
            
            try {
                const errorBody = await response.text();  // or response.json() if you expect JSON
                errorMessage += ` | Response: ${errorBody}`;
            } catch (e) {
                errorMessage += ' | Failed to read response body.';
            }

            throw new Error(errorMessage);
        }

        generic_alert(`Client ${method === 'POST' ? 'created' : 'updated'} successfully.`, reload=true);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
};




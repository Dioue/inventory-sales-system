// API Fetch
let _AllCategory = null;

const fetchAllCategory = async () => {
    try {
        const response = await fetch(`/api/category/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch batch: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching batch:', error);
        throw error;
    }
}

const fetchCatId = async (id) => {
    try {
        const response = await fetch(`/api/category/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch batch (ID: ${id}): ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching batch:', error);
        throw error;
    }
}

// Load necessary API on DOM load
document.addEventListener('DOMContentLoaded', async () => {
    _AllCategory = await fetchAllCategory()
})

// THIS IS SO I CAN SEE THE IMPLEMENTATION DO NOT REMOVE :D JOE BECAUSE I AM DIZZY OMG
// THIS IS SO I CAN SEE THE IMPLEMENTATION DO NOT REMOVE :D JOE BECAUSE I AM DIZZY OMG
// THIS IS SO I CAN SEE THE IMPLEMENTATION DO NOT REMOVE :D JOE BECAUSE I AM DIZZY OMG
// DOM Access
const modalCreateBtn = document.querySelector('.item-create-btn');
const modalUpdateBtns = document.querySelectorAll('.category-edit');
const categoryForm = document.getElementById('category-form');
const submitBtn = document.getElementById('category-submit');
const confirmModal = document.getElementById('confirm-category');
const confirmBtn = document.getElementById('confirm-submit');
const confirmHide = document.querySelectorAll('.confirm-category-hide');
const modalHideBtn = document.querySelector('.category-form-hide-btn');
const modalOptions = {'backdrop': 'static'};
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value; 

// Category form fields
const formId = document.querySelector('.category-form-id');
const catName = document.getElementById('category-name');
const catCode = document.getElementById('category-code');

modalCreateBtn.addEventListener('click', async () => {
    const cat = await fetchAllCategory();
    const maxId = Math.max(...cat.map(category => category.id), 0) + 1;
    formId.innerText = `CN-${(maxId).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})}`;
    catName.value = '';
    catCode.value = '';

    const handleSubmit = async () => {
        new Modal(confirmModal, modalOptions).show();
        const handleConfirmClick = async () => {
            await categoryAPI('POST');
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
    new Modal(categoryForm, modalOptions).show();

    const handleModalHide = () => {
        new Modal(categoryForm, modalOptions).hide();
        submitBtn.removeEventListener('click', handleSubmit);
        modalHideBtn.removeEventListener('click', handleModalHide);
    };

    modalHideBtn.addEventListener('click', handleModalHide, { once: true });
});

// Modal for Update
modalUpdateBtns.forEach(el => {
    el.addEventListener('click', async (event) => {
        const id = event.currentTarget.dataset.id;
        const cat = await fetchCatId(id);

        formId.innerText = `CN-${cat.id}`;
        catName.value = cat.name;
        catCode.value = cat.code;

        const handleSubmit = async () => {
            new Modal(confirmModal, modalOptions).show();
            const handleConfirmClick = async () => {
                await categoryAPI('PUT', id);
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
        new Modal(categoryForm,modalOptions).show();

        const handleModalHide = () => {
            new Modal(categoryForm,modalOptions).hide();
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
const categoryAPI = async (method, id = null) => {
    const name = sanitizer(catName.value);
    const code = sanitizer(catCode.value);

    if (!name) {
        alert('Please add a valid category name.');
        return;
    } else if(!code) {
        alert('Please add a valid category code.');
        return;
    }

    const payload = { name, code };
    const url = id ? `/api/category/${id}/` : '/api/category/';

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
            throw new Error(`Failed to ${method === 'POST' ? 'create' : 'update'} category.`);
        }

        alert(`Category ${method === 'POST' ? 'created' : 'updated'} successfully.`);
        location.reload();
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
};




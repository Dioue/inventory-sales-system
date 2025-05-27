const productUpdateButton = document.querySelectorAll('.product-update-btn');
const updateForm = document.querySelector('#product-update');
const updateFormHide = document.querySelector('#product-update-hide');
const updateFormSubmit = document.querySelector('#product-update-submit');
const confirmModal = document.querySelector('#confirm-product-update');
const confirmBtn = document.querySelector('#confirm-product-update-submit');
const confirmHide = document.querySelectorAll('.confirm-product-update-hide');
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

const modalOptions = {'backdrop': 'static'};
// Update Form Elements
const formId = document.querySelector('.product-update-id');
const formName = document.querySelector('#product-update-name');
const formCode = document.querySelector('#product-update-code');
const formApplication = document.querySelector('#product-update-application');
const formSide = document.querySelector('#product-update-side');
const formCategory = document.querySelector('#product-update-category');
const formDescription = document.querySelector('#product-update-description');
const formCost = document.querySelector('#product-update-cost');
const formSelling = document.querySelector('#product-update-selling');
const formUnit = document.querySelector('#product-update-unit');
const formCrit = document.querySelector('#product-update-critical');

// API
const fetchProductId = async (id) => {
    try {
        const response = await fetch(`/api/products/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch product ${id}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching product ${id}: `, error);
        throw error;
    }
}

const checkProductExists = async (name, code, id = null) => {
    const params = new URLSearchParams();
    if (name) params.append('name', name);
    if (code) params.append('code', code);
    if (id) params.append('id', id);

    const response = await fetch(`/api/products/exists/?${params.toString()}`);
    if (!response.ok) throw new Error('Error checking for product existence.');
    const data = await response.json();
    return data.exists;
};

// DOM handlers
productUpdateButton.forEach(el => {
    el.addEventListener('click', async (event) => {
        const targetProduct = await fetchProductId(event.currentTarget.dataset.id);
        formId.innerText = `PN-${targetProduct.id}`;
        formName.value = targetProduct.name;
        formCode.value = targetProduct.code;
        formApplication.value = targetProduct.application;
        formDescription.value = targetProduct.description;
        formCost.value = targetProduct.cost_price;
        formSelling.value = targetProduct.selling_price;
        formCategory.value = targetProduct.category;
        formSide.value = targetProduct.side;
        formUnit.value = targetProduct.unit;
        formCrit.value = targetProduct.critical_level;

        // Show/hide behavior
        const handleSubmit = async () => {
            new Modal(confirmModal, modalOptions).show();
            const handleConfirmClick = async () => {
                new Modal(confirmModal, modalOptions).hide();
                await productAPI('PUT', targetProduct.id);
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
            new Modal(updateForm, modalOptions).hide();
            updateFormSubmit.removeEventListener('click', handleSubmit);
            updateFormHide.removeEventListener('click', handleModalHide);
        };
        updateFormSubmit.addEventListener('click', handleSubmit);
        updateFormHide.addEventListener('click', handleModalHide, { once: true });
        new Modal(updateForm, modalOptions).show();
    })
})


// Sanitizer to remove all input related mf that can inject code to the database (special characters and trailing whitespaces. Not including inner spaces)
function sanitizer(input) {
    return input.trim().replace(/[^a-zA-Z0-9\s-]/g, '');
}

// API for POST and PUT
const productAPI = async (method, id = null) => {
    const name = sanitizer(formName.value);
    const code = sanitizer(formCode.value);
    const application = sanitizer(formApplication.value);
    const description = sanitizer(formDescription.value);
    const cost_price = formCost.value;
    const selling_price = formSelling.value;
    const side = formSide.value;
    const category = formCategory.value;
    const unit = formUnit.value;
    const crit = formCrit.value;

    // Validations
    if (!name || !code || !category || !unit) {
        generic_alert('Please fill in all required fields.');
        return;
    }

    if (parseFloat(cost_price) > parseFloat(selling_price)) {
        generic_alert('Cost price cannot be greater than selling price.');
        return;
    }

    try {
        const duplicateExists = await checkProductExists(name, code, id);
        if (duplicateExists) {
            generic_alert('Product name or code already exists.');
            return;
        }

        const payload = {
            name, code, application, description,
            cost_price, selling_price, side,
            category, unit, critical_level: crit
        };

        const url = id ? `/api/products/${id}/` : '/api/products/';
        const headers = { 'X-CSRFToken': csrfToken };
        const body = new FormData();

        Object.entries(payload).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                body.append(key, value);
            }
        });

        const response = await fetch(url, {
            method,
            headers,
            body
        });

        if (!response.ok) throw new Error(`Failed to ${method === 'POST' ? 'create' : 'update'} the product.`);

        generic_alert(`Product ${method === 'POST' ? 'created' : 'updated'} successfully.`, reload = true);
    } catch (error) {
        generic_alert(error.message || 'Something went wrong.');
    }
};



document.getElementById('create-product-btn').addEventListener('click', function (event) {
    const form = document.getElementById('product_create_form');

    if (!form.checkValidity()) {
        alert('Please correctly fill in all the fields before submitting.');
        event.preventDefault();
    } else {
        const modal = document.getElementById('confirm_create');
        modal.click();
    }
});

document.getElementById('confirm_product_submit').addEventListener('click', async function (event) {
    const form = document.getElementById('product_create_form');
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    event.preventDefault();

    const formData = new FormData(form);

    try {
        const response = await fetch("/api/products/", {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        });


        if (response.ok) {
            const responseData = await response.json();
            console.log('Product created successfully', responseData);
            showAlert(
                'info',
                'Product created successfully',
                'Would you like to create another product entry?',
                true
            );
        } else {
            const errorData = await response.json();
            console.error('Error creating product:', errorData);

            let formattedMessage = Object.entries(errorData)
                .map(([field, messages]) => {
                    if (messages.length > 0) {
                        
                        return `${field}: ${messages[0]
                            .replace(/(^\w{1}|\.\s*\w{1})/gi, match => match.toUpperCase())}`;
                    }
                })
                .join('<br>');

            showAlert('error', 'Unsuccessful product entry', formattedMessage);
        }
    } catch (error) {
        console.error('Network error:', error);
        showAlert('error', 'Network Error', 'Please try again later.');
    }
});

const showAlert = (() => {
    const alert = document.getElementById('alert');
    const alertHeader = document.getElementById('alert-header');
    const alertText = document.getElementById('alert-text');
    const alertIconPath = document.getElementById('alert-icon-path');
    const alertAdd = document.getElementById('alert-add');
    const alertDismiss = document.getElementById('alert-dismiss');

    const resetForm = () => {
        document.getElementById('product_create_form').reset();
        closeAlert();
    };

    const closeAlert = () => {
        alert.classList.add('opacity-0');
        setTimeout(() => {
            alert.classList.add('hidden');
        }, 300); // Match this with your CSS transition duration
    };

    alertAdd.addEventListener('click', resetForm);
    alertDismiss.addEventListener('click', closeAlert);

    return (type, header, message, hasAction = false) => {
        alert.className = `p-4 mb-4 border rounded-lg hidden opacity-0 ${
            type === 'info'
                ? 'text-blue-800 border-blue-300 bg-blue-50 dark:bg-gray-800 dark:text-blue-400 dark:border-blue-800'
                : 'text-red-800 border-red-300 bg-red-50 dark:bg-gray-800 dark:text-red-400 dark:border-red-800'
        }`;

        alertIconPath.setAttribute(
            'd',
            type === 'info'
                ? 'M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 1 1v4h1a1 1 0 1 1 0 2Z'
                : 'M10 1.5A8.5 8.5 0 1 0 18.5 10 8.5 8.5 0 0 0 10 1.5ZM9 13h2V11H9Zm0-4h2V5H9Z'
        );

        alertDismiss.className = `${
            type === 'info' ?
            'text-blue-800 bg-transparent border border-blue-700 font-medium rounded-lg text-xs px-3 py-1.5 text-center' 
            : 'text-red-800 bg-transparent border border-red-700 font-medium rounded-lg text-xs px-3 py-1.5 text-center'}`;

        alertHeader.innerText = header;
        alertText.innerHTML = message;

        if (hasAction) {
            alertAdd.classList.remove('hidden');
        } else {
            alertAdd.classList.add('hidden');
        }

        alert.classList.remove('hidden');
        alert.classList.remove('opacity-0');
    };
})();

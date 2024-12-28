
document.getElementById('create-product-btn').addEventListener('click', function(event) {
    const form = document.getElementById('product_create_form');

    if (!form.checkValidity()) {
        alert('Please correctly fill in all the fields before submitting.');
        event.preventDefault();
    } else {
        const modal = document.getElementById('confirm_create')
        modal.click();
    }
});


document.getElementById('confirm_product_submit').addEventListener('click', async function(event) {
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
            console.log('Product created successfully', responseData)
            showAlertInfo('Product created successfully', 'Would you like to create another product entry?')
            
        } else {
            const errorData = await response.json();
            console.error('Error creating product:', errorData);

           // Format the error message
            let formattedMessage = '';
            for (const [field, messages] of Object.entries(errorData)) {
                if (messages.length > 0) {
                    formattedMessage += `<strong>${field}:</strong><br>`; // Add the field name
                    formattedMessage += `${messages[0]}<br><br>`;  // Show only the first error message and add a line break
                }
            }

            // Call your function to show the formatted error message
            showAlertError('Unsuccessful product entry', formattedMessage);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
});


const showAlertInfo = (header, message) => {
    const _alert_info = document.getElementById('alert-info');
    const _header = document.getElementById('alert-info-header');
    const _text = document.getElementById('alert-info-text');
    const _add = document.getElementById('alert-info-add');
    const _dismiss = document.getElementById('alert-info-dismiss');

    // Ensure the alert is visible and no opacity transition is in progress
    _alert_info.classList.remove('hidden');
    _alert_info.classList.remove('opacity-0'); // Remove any opacity class to ensure visibility

    // Update the content of the alert
    _header.innerText = header;
    _text.innerHTML = message;

    // Remove event listeners to prevent duplicates
    _add.removeEventListener('click', resetForm);
    _dismiss.removeEventListener('click', closeAlert);

    // Add event listeners
    _add.addEventListener('click', resetForm);
    _dismiss.addEventListener('click', closeAlert);

    function resetForm() {
        document.getElementById('product_create_form').reset();
        _alert_info.classList.add('hidden'); // Hide the alert after action
    }

    function closeAlert() {
        // Hide the alert and apply opacity-0 for transition
        _alert_info.classList.add('opacity-0');
        
        // Wait for transition to finish before fully hiding the element
        setTimeout(() => {
            _alert_info.classList.add('hidden'); // Finally hide the element
        }, 300); // Adjust the timeout to match your transition duration (300ms for example)
    }
};

const showAlertError = (header, message) => {
    const _alert_error = document.getElementById('alert-error');
    const _header = document.getElementById('alert-error-header');
    const _text = document.getElementById('alert-error-text');
    const _dismiss = document.getElementById('alert-error-dismiss');

    // Ensure the alert is visible and no opacity transition is in progress
    _alert_error.classList.remove('hidden');
    _alert_error.classList.remove('opacity-0'); // Remove any opacity class to ensure visibility

    // Update the content of the alert
    _header.innerText = header;
    _text.innerHTML = message;

    // Remove event listeners to prevent duplicates
    _dismiss.removeEventListener('click', closeAlert);

    // Add event listener
    _dismiss.addEventListener('click', closeAlert);

    function closeAlert() {
        // Hide the alert and apply opacity-0 for transition
        _alert_error.classList.add('opacity-0');
        
        // Wait for transition to finish before fully hiding the element
        setTimeout(() => {
            _alert_error.classList.add('hidden'); // Finally hide the element
        }, 300); // Adjust the timeout to match your transition duration (300ms for example)
    }
};

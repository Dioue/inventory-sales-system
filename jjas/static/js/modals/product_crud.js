
document.getElementById('create-product-btn').addEventListener('click', function(event) {
    // Prevent the default action of toggling the modal if inputs are empty
    const form = document.getElementById('product_create_form');

    if (!form.checkValidity()) {
        alert('Please fill in all the fields before submitting.');
        event.preventDefault(); // Prevent the modal toggle if not all fields are filled
    } else {
        const modal = document.getElementById('confirm_create')
        modal.click();
    }
});



document.getElementById('confirm_product_submit').addEventListener('click', async function(event) {
    // Prevent the default action of toggling the modal if inputs are empty
    const form = document.getElementById('product_create_form');
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    event.preventDefault(); // Prevent the default form submission

    // Gather form data
    const formData = new FormData(form);

    // Send the form data to the backend asynchronously
    try {
        const response = await fetch("/api/products/", {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,  // Include CSRF token in the headers
            },
            body: formData,  // Form data that includes the product details
        });

        if (response.ok) {
            // Handle the successful creation of the product (e.g., display a success message)
            const responseData = await response.json();
            console.log('Product created successfully:', responseData);
            
            // Optionally close the modal after successful submission
            document.getElementById('product_create').classList.add('hidden');
        } else {
            // Handle errors (e.g., invalid data, server issues)
            const errorData = await response.json();
            console.error('Error creating product:', errorData);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
});
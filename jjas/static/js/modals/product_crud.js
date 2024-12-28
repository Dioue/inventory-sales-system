document.addEventListener('DOMContentLoaded', function () {
    const productForm = document.querySelector('#product_create_form');  // Your product create form
    const submitButton = document.querySelector('#product_submit_form'); // Submit button

    // Get the CSRF token from the page
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    productForm.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Gather form data
        const formData = new FormData(productForm);

        // Append CSRF token to the form data
        formData.append('csrfmiddlewaretoken', csrfToken);

        // Send the form data to the backend asynchronously
        try {
            const response = await fetch("{% url 'api:product-list' %}", {
                method: 'POST',
                body: formData,
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
});


document.getElementById('create-product-btn').addEventListener('click', function(event) {
    const form = document.getElementById('product_create_form');

    if (!form.checkValidity()) {
        alert('Please fill in all the fields before submitting.');
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
            popGeneric('Product created successfully', responseData)
            
            
        } else {
            const errorData = await response.json();
            console.error('Error creating product:', errorData);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
});



const popGeneric = (header, message) => {
    const _header = document.getElementById('popup_generic_header')
    const _message = document.getElementById('popup_generic_message')
    const _btn = document.getElementById('popup_generic_btn')
    const _dismiss = document.getElementById('popup_generic_dismiss')
    const _add = document.getElementById('popup_generic_add')

    _header.innerText = header
    _message.innerText = message
    _btn.click()
    
    _add.addEventListener('click', ()=> {
        const form = document.getElementById('product_create_form');
        const product_id = document.getElementById('product_create_id');

        form.reset();
        document.getElementById('popup_generic').classList.add('hidden');
    })

    _dismiss.addEventListener('click', ()=> {
        document.getElementById('popup_generic').classList.add('hidden');
    })

}
const editModal = async (productId) =>{
    const apiUrl = `/api/products/${productId}/`;
    try {
        
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        });
        
        if (response.ok) {
            const product = await response.json();

            document.getElementById('edit_name').value = product.name || '';
            document.getElementById('edit_code').value = product.code || '';
            document.getElementById('edit_application').value = product.application || '';
            document.getElementById('edit_side').value = product.side || '';
            document.getElementById('edit_cost_price').value = product.cost_price || 0;
            document.getElementById('edit_selling_price').value = product.selling_price || 0;
            document.getElementById('edit_quantity_left').value = product.quantity_left || 0;
            document.getElementById('edit_unit').value = product.unit || '';
            document.getElementById('edit_category').value = product.category || '';
            document.getElementById('edit_critical_level').value = product.critical_level || 0;
            document.getElementById('edit_description').value = product.description || '';
            document.getElementById('edit_supplier').value = product.supplier || '';

            const modal = document.getElementById('view_modal');
            modal.classList.remove('hidden');
            modal.classList.add('flex');

        } else {
            alert('Failed to retrieve the product.');
            console.error('Error:', await response.text());
        }

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while fetching the product.');
    }
}

// Close edit modal function
document.querySelectorAll('[data-modal-toggle="view_modal"]').forEach((button) => {
    button.addEventListener('click', () => {
        const modal = document.getElementById('view_modal');
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    });
});
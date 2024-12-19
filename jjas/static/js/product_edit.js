function populateModal(button) {
    // Get the data attributes from the button
    var id = button.getAttribute('data-id');
    var name = button.getAttribute('data-name');
    var code = button.getAttribute('data-code');
    var application = button.getAttribute('data-application');
    var side = button.getAttribute('data-side');
    var cost_price = button.getAttribute('data-cost_price');
    var selling_price = button.getAttribute('data-selling_price');
    var quantity_left = button.getAttribute('data-quantity_left');
    var unit = button.getAttribute('data-unit');
    var category = button.getAttribute('data-category');
    var critical_level = button.getAttribute('data-critical_level');
    var description = button.getAttribute('data-description');
    var supplier = button.getAttribute('data-supplier');
    var image = button.getAttribute('data-image');
    
    // Populate the modal fields with the data
    document.getElementById('name').value = name;
    document.getElementById('code').value = code;
    document.getElementById('bn').innerHTML = `BN: ${id}`;
    document.getElementById('application').value = application;
    document.getElementById('side').value = side;
    document.getElementById('cost_price').value = cost_price;
    document.getElementById('selling_price').value = selling_price;
    document.getElementById('quantity_left').value = quantity_left;
    document.getElementById('unit').value = unit;
    document.getElementById('category').value = category;
    document.getElementById('critical_level').value = critical_level;
    document.getElementById('description').value = description;
    document.getElementById('supplier').value = supplier;
    // Set the image (if exists)
    if (image) {
        document.querySelector('.modal img').src = image;
    } else {
        document.querySelector('.modal img').src = '/static/img/no_image.jpg'; // fallback
    }
    
}

document.querySelectorAll('[data-modal-toggle]').forEach(button => {
    button.addEventListener('click', function() {
        const modal = document.getElementById(this.getAttribute('data-modal-toggle'));
        modal.classList.toggle('hidden');
    });
});
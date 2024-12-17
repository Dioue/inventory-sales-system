function toggleAll(source) {
    const checkboxes = document.querySelectorAll('input[name="selected_items"]');
    checkboxes.forEach((checkbox) => {
        checkbox.checked = source.checked;
    });
}
const toggleAll = (source) => {
    const checkboxes = document.querySelectorAll('input[name="selected_items"]');
    checkboxes.forEach((checkbox) => {
        checkbox.checked = source.checked;
    });
}

// Function to update the selected product count
const updateSelectedCount = () => {
    let checkedItems = document.querySelectorAll('input.checkbox_helper:checked');
    let selectedCount = checkedItems.length;

    let message = document.getElementById('delete-modal-text');
    let buttonId = document.getElementById('delete_button_modal');
    let buttonAll = document.getElementById('checkbox-all');
    let allCheckboxes = document.querySelectorAll('.checkbox_helper');

    // Bail out early if the delete modal isn't on this page
    if (!buttonId || !message) {
        return;
    }

    let isSelectAllChecked = buttonAll && buttonAll.checked;

    if (allCheckboxes.length !== selectedCount) {
        if (buttonAll) buttonAll.checked = false;
    } else if (selectedCount > 0) {
        if (buttonAll) buttonAll.checked = true;
    }

    if (selectedCount === 0 && !isSelectAllChecked) {
        buttonId.classList.add('cursor-not-allowed');
        buttonId.disabled = true;
        message.innerHTML = 'Please select an item to delete.';
    }
    else if (selectedCount > 1 || isSelectAllChecked) {
        message.innerHTML = `Are you sure you want to delete ${selectedCount} items?`;
        buttonId.classList.remove('cursor-not-allowed');
        buttonId.disabled = false;
    }
    else {
        message.innerHTML = 'Are you sure you want to delete this item?';
        buttonId.classList.remove('cursor-not-allowed');
        buttonId.disabled = false;
    }
};


// Attach event listener to "select all" checkbox
let selectAllCheckbox = document.getElementById('checkbox-all');
if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function () {
        let allCheckboxes = document.querySelectorAll('.checkbox_helper');
        allCheckboxes.forEach(function (checkbox) {
            checkbox.checked = selectAllCheckbox.checked;
        });
        updateSelectedCount();
    });
}

// Attach event listeners to the checkboxes
document.querySelectorAll('.checkbox_helper').forEach(function (checkbox) {
    checkbox.addEventListener('change', updateSelectedCount);
});

// Initial update (in case any checkboxes are pre-checked)
updateSelectedCount();


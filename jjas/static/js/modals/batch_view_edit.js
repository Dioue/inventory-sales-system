
// show a view quackity quack
const view = document.querySelectorAll('.batch_view');
const edit = document.querySelectorAll('.batch_edit');
const modalView = document.getElementById('default_item_view');
const modalEdit = document.getElementById('what');
const modalHideButton = document.querySelector('.default_item_view_hide');
const setStatic = {"backdrop": "static"}
// Function to fetch product details
async function fetchBatchDetails(id) {
    try {
        const response = await fetch(`/api/batch-orders/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch batch (ID: ${id}): ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching batch:', error);
        throw error;
    }
}


// Function to handle view button click
async function handleViewClick(event) {
    const id = event.currentTarget.dataset.id;
    if (id) {
        try {
            const batch = await fetchBatchDetails(id);
            console.log(batch);
            const header_id = document.querySelector('.default_view_header_id');
            const supplier_name = document.getElementById('view_sn');
            const purchase_date = document.getElementById('view_pd');

            header_id.innerText = `BN-${batch.id}`;
            supplier_name.innerText = batch.supplier
            purchase_date.innerText = batch.purchase_date

            new Modal(modalView, setStatic).show();
        } catch (error) {
            console.error('Error handling view click:', error);
        }
    }
}


// Function to handle edit button click
async function handleEditClick(event) {
    const id = event.currentTarget.dataset.id;
    if (id) {
        try {
            const batch = await fetchBatchDetails(id);
            console.log(product);

            new Modal(modalView).show();
        } catch (error) {
            console.error('Error handling view click:', error);
        }
    }
}

// Attach Event Listeners to View Buttons
view.forEach(el => el.addEventListener('click', handleViewClick));
modalHideButton.addEventListener('click', () => new Modal(modalView, setStatic).hide());


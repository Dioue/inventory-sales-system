
// show a view quackity quack
const view = document.querySelectorAll('.batch_view');
const edit = document.querySelectorAll('.batch_edit');
const modalView = document.getElementById('default_item_view');
const modalEdit = document.getElementById('what');
const modalHideButton = document.querySelector('.default_item_view_hide');
const setStatic = {"backdrop": "static"}
let dataTableInstance = null;

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

async function handleViewClick(event) {
    const id = event.currentTarget.dataset.id;
    if (id) {
        try {
            const batch = await fetchBatchDetails(id);
            const header_id = document.querySelector('.default_view_header_id');
            const batch_id = document.getElementById('view_batch_id');
            const grand_total = document.getElementById('view_gt');
            const supplier_name = document.getElementById('view_sn');
            const purchase_date = document.getElementById('view_pd');

            // Update modal fields
            header_id.innerText = `BN-${batch.id}`;
            batch_id.innerText = batch.id;
            grand_total.innerText = parseFloat(batch.grand_total).toLocaleString('en-US', { style: 'currency', currency: 'PHP' });
            supplier_name.innerText = batch.supplier;
            purchase_date.innerText = batch.purchase_date;

            const tableBody = document.querySelector('#batch-view-table tbody');
            if (batch.items.length > 0) {
                tableBody.innerHTML = '';
                const fragment = document.createDocumentFragment();
                batch.items.forEach(item => {
                    const row = document.createElement('tr');
                    Object.values(item).forEach(value => {
                        const td = document.createElement('td');
                        td.textContent = value;
                        row.appendChild(td);
                    });
                    fragment.appendChild(row);
                });
                tableBody.appendChild(fragment);


                // Attach the simpleDatatables library. This shit is awesome! 
                if (typeof simpleDatatables.DataTable !== 'undefined') {
                    if (!tableBody.classList.contains('initialized')) {
                        dataTableInstance = new simpleDatatables.DataTable("#batch-view-table", {
                            searchable: true,
                            sortable: true,
                            perPageSelect: false
                        });

                    }
                }
            }
            
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
            new Modal(modalView).show();
        } catch (error) {
            console.error('Error handling view click:', error);
        }
    }
}

function handleModalHide() {
    if (dataTableInstance) {
        dataTableInstance.destroy();
        dataTableInstance = null;
    }
}

view.forEach(el => el.addEventListener('click', handleViewClick));
modalHideButton.addEventListener('click', () => {
    new Modal(modalView, setStatic).hide();
    handleModalHide();
});
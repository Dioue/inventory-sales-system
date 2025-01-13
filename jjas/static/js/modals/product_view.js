const viewBtn = document.querySelectorAll('.product-view-btn');
const viewId = document.querySelector('.product_view_header_id');
const viewModal = document.getElementById('product_view');
const viewModalHide = document.querySelector('.product_view_hide');
const viewName = document.getElementById('view_name');
const viewCode = document.getElementById('view_code');
const viewCategory = document.getElementById('view_category');
const viewApplication = document.getElementById('view_application');
const viewQuantity = document.getElementById('view_quantity');
const viewCost = document.getElementById('view_cost');
const viewCritical = document.getElementById('view_critical');
const viewStatus = document.getElementById('view_status');
const viewSelling = document.getElementById('view_selling');
let _viewCategory = null;
let _viewUnits = null;

// API
const fetchProducts = async (id = null) => {
    try {
        const url = id === null ? `/api/products/` : `/api/products/${id}/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch product: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching product: `, error);
        throw error;
    }
}

const fetchUnits = async (id = null) => {
    try {
        const url = id === null ? `/api/units/` : `/api/units/${id}/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch units: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching units: `, error);
        throw error;
    }
}

const fetchCategory = async (id = null) => {
    try {
        const url = id === null ? `/api/category/` : `/api/category/${id}/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch category: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching category: `, error);
        throw error;
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    _viewCategory = await fetchCategory();
    _viewUnits = await fetchUnits();
})



// DOM controllers/listeners
viewBtn.forEach(el => {
    el.addEventListener('click', async (event) => {
        const id = event.target.dataset.id;
        const product = await fetchProducts(id);
        viewId.innerText = `PN-${id}`

        if (product) {
            const _category = _viewCategory.find(cat => cat.id === product.category);
            const _unit = _viewUnits.find(unit => unit.id === product.unit)

            const costPrice = parseFloat(product.cost_price);
            const sellingPrice = parseFloat(product.selling_price);
            viewName.innerText = product.name || 'N/A';
            viewCode.innerText = product.code || 'N/A';
            viewCategory.innerText = `${_category.code} - ${_category.name}` || 'N/A';
            viewApplication.innerText = product.application || 'N/A';
            viewQuantity.innerText = `${product.quantity || '0'} ${_unit.name || ''}`;
            viewCost.innerText = `₱${!isNaN(costPrice) ? costPrice.toFixed(2) : '0.00'}`;
            viewCritical.innerText = product.critical_level || 'N/A';
            viewStatus.innerText = product.status || 'N/A';
            viewSelling.innerText = `₱${!isNaN(sellingPrice) ? sellingPrice.toFixed(2) : '0.00'}`;  
          } 


          const _tableBodyProductView = document.querySelector('#product-view-table tbody');

            // Attach the simpleDatatables library. This is awesome! 
            if (typeof simpleDatatables.DataTable !== 'undefined')  {
                dataTableInstance = new simpleDatatables.DataTable("#product-view-table", {
                    searchable: true,
                    sortable: true,
                    perPageSelect: false
                });

            }


        const handleModalHide = () => {
            new Modal(viewModal, modalOptions).hide();
            viewModalHide.removeEventListener('click', handleModalHide);
        };

        viewModalHide.addEventListener('click', handleModalHide);
        new Modal(viewModal, modalOptions).show();  
    })
})
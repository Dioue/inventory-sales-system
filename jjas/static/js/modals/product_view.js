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
let _populatedProductView;

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

const fetchFilteredProductsReadOnly = async (query) => {
    try {
        const url = `/api/products-readonly/search/?query=${encodeURIComponent(query)}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch search results: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching filtered products:', error);
        return [];
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    _viewCategory = await fetchCategory();
    _viewUnits = await fetchUnits();
})

// DOM controllers/listeners
viewBtn.forEach(el => {
    el.addEventListener('click', async (event) => {
        const id = event.currentTarget.dataset.id;
        const product = await fetchFilteredProductsReadOnly(id);
        viewId.innerText = `PN-${id}`

        if (product) {
            const costPrice = parseFloat(product[0].cost_price);
            const sellingPrice = parseFloat(product[0].selling_price);
            viewName.innerText = product[0].name || 'N/A';
            viewCode.innerText = product[0].code || 'N/A';
            viewCategory.innerText = `${product[0].category.code} - ${product[0].category.name}` || 'N/A';
            viewApplication.innerText = product[0].application || 'N/A';
            viewQuantity.innerText = `${product[0].quantity || '0'} ${product[0].unit.name || ''}`;
            viewCost.innerText = `₱${!isNaN(costPrice) ? costPrice.toFixed(2) : '0.00'}`;
            viewCritical.innerText = product[0].critical_level || 'N/A';
            viewStatus.innerText = product[0].status || 'N/A';
            viewSelling.innerText = `₱${!isNaN(sellingPrice) ? sellingPrice.toFixed(2) : '0.00'}`;
            _populatedProductView = true;
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
        if(_populatedProductView)
        {
            new Modal(viewModal, modalOptions).show();  
        }
    })
})
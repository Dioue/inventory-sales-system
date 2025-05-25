const productBadge = document.getElementById('product-badge');
const inventoryBadge = document.getElementById('inventory-badge');

const fetchCritical = async () => {
    try {
        const url = `/api/products-readonly/critical/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch critical results: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching critical products:', error);
        return { critical_count: 0 };
    }
};

fetchCritical().then(data => {
    const count = data.critical_count;

    if (count > 0) {
        productBadge.textContent = count;
        inventoryBadge.textContent = count;

        productBadge.classList.remove('hidden');
        inventoryBadge.classList.remove('hidden');
    } else {
        productBadge.classList.add('hidden');
        inventoryBadge.classList.add('hidden');
    }
});

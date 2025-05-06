const showProjectionBtn = document.querySelector('.generate-projection-btn');
const projectionBadge = document.querySelector('.generate-projection-text-badge');
const projectionModal = document.querySelector('#generate-projection');
const projectionModalHide = document.querySelector('#generate-projection-hide');
const selectedProjection = document.querySelector('#last-month-projection');

showProjectionBtn.addEventListener('click', () => {

    const selectedProjectionValue = selectedProjection.options[selectedProjection.selectedIndex].text;
    projectionBadge.textContent = selectedProjectionValue;

    const handleModalHide = () => {
        new Modal(projectionModal, modalOptions).hide();
        projectionModalHide.removeEventListener('click', handleModalHide);
    };
    projectionModalHide.addEventListener('click', handleModalHide, { once: true });
    new Modal(projectionModal, modalOptions).show();
})

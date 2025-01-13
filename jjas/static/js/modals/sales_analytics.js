const showInsightBtn = document.querySelectorAll('.show-insight-btn');
const insightModal = document.querySelector('#product-insight');
const insightModalHide = document.querySelector('#product-insight-hide');
const modalOptions = {'backdrop': 'static'};



showInsightBtn.forEach(el => {
    el.addEventListener('click', () => {


        const handleModalHide = () => {
            new Modal(insightModal, modalOptions).hide();
            insightModalHide.removeEventListener('click', handleModalHide);
        };
        insightModalHide.addEventListener('click', handleModalHide, { once: true });
        new Modal(insightModal, modalOptions).show();
    })
})
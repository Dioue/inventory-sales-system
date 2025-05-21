const salesReportBtn = document.querySelector('.show-sales-report');
const salesReportModal = document.querySelector('#sales-report');
const salesReportHide = document.querySelector('#sales-report-hide');

salesReportBtn.addEventListener('click', () => {

    const handleModalHide = () => {
        new Modal(salesReportModal, { backdrop: 'static' }).hide();
        salesReportHide.removeEventListener('click', handleModalHide);
    };
    salesReportHide.addEventListener('click', handleModalHide, { once: true });

    new Modal(salesReportModal, { backdrop: 'static' }).show();
});
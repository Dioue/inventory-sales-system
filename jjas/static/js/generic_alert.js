const generic_alert = (message = "Something went wrong, please try again later.", reload = false) => {
    const alertForm = document.querySelector('#generic-alert');
    const alertBtn = document.querySelector('.generic-alert-btn');
    const alertContent = document.querySelector('.generic-alert-content');
    const modalOptions = {'backdrop': 'static'}

    alertContent.innerText = message;

    alertBtn.addEventListener('click', () => {
        new Modal(alertForm, modalOptions).hide();
        if(reload){
            location.reload();
        }
    }, {once: true})

    new Modal(alertForm, modalOptions).show();
}
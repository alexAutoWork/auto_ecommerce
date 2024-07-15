const $ = require('jquery');
const {reset} = require('./reset');
const {toggle_element_slide} = import('../shared/shared_event_func.mjs');

let is_logged_in = false;

$(() => {
    [is_logged_in] = check_user();
    if (is_logged_in) {
        window.location.replace = 'http://host.docker.internal:8000/account/details';
    }
})

$('#reset_type_select_submit').on('click', () => {
    let reset_type = $(`input[name='reset_type']`).filter(':checked').val();
    const current_cont = $('#reset_email_password_cont');
    toggle_element_slide('next', reset_type);
    reset(reset_type, '/forgot', false);
})
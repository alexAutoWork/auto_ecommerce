const $ = require('jquery');
const {reset} = require('./reset');
import {gen_func} from '../shared/shared_gen_func';
import {event_func} from '../shared/shared_event_func';
const {check_user} = require('./sens');
const {global} = require('../../config');

let user_state = [false, false]

$(() => {
    user_state = check_user();
    if (user_state[0] === true) {
        gen_func.redirect(`${global.ngrok_frontend_url}/account/details/`);
    }
})

$('#reset_type_select_submit').on('click', () => {
    let reset_type = $(`input[name='reset_type']`).filter(':checked').val();
    const current_cont = $('#reset_email_password_cont');
    event_func.toggle_slide('next', reset_type);
    reset(reset_type, '/forgot');
})
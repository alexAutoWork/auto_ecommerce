const $ = require('jquery');
const axios = require('axios');
const {reset} = require('./reset');
const {check_user} = require('./sens');
import {gen_func} from '../shared/shared_gen_func';
const {global} = require('../../config.js');

let user_state = [false, false]

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: get_details});
})

function get_details() {
    axios.get(`${global.ngrok_api_url}/user/details/`, global.options)
    .then((res) => {
        data = res.data;
        for (let [key, value] of Object.entries(data)) {
            let cont = $(`[data-field-type='${key}']`);
            cont.find('.my_account_initial_value').text(value);
            cont.find(`input[name='my_account_details_edit_${key}']`).val(value);
        }
    })
    .catch((err) => {
        console.log(err);
    })
}

$('.my_account_details_edit_btn').on('click', () => {
    const field_type = $(this).closest('[data-field-type]');
    const popup = `my_account_details_${field_type}_popup`;
    $(popup).modal('show');
    if (field_type === 'email' || 'password') {
        $('.my_account_details_reset').on('click', () => {
            $(popup).modal('hide');
            $('.my_account_details_reset_popup').modal('show')
            if (field_type === 'password') {
                $('#reset_select_method_cont').show();
            }
            if (field_type === 'email') {
                $('#verify_mobile_no_method_cont').show();
            }
            reset(field_type, '/user/details');
        })
    }
    else {
        const initial_value = $(this).closest('.my_account_initial_value').text();
        $('.my_account_details_submit').on('click', () => {
            let changed_value = $(`input[name='my_account_details_edit_${field_type}']`).val();
            if (changed_value !== initial_value) {
                const data = {[field_type]: changed_value};
                axios.patch(`${global.ngrok_api_url}/user/details/`, global.options)
                .then((res) => {
                    console.log(res.data.message);
                    location.reload();
                })
                .catch((err) => {
                    console.log(err);
                })
            }
        })
    }
})
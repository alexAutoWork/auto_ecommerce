const $ = require('jquery');
const axios = require('axios');
const {reset} = require('./reset');
const {check_user} = require('./sens');

let is_logged_in = false;
let withCredentials = false;

$(() => {
    [is_logged_in, withCredentials] = check_user();
    if (is_logged_in) {
        axios.get('/user/details/', {withCredentials: withCredentials})
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
    else {
        window.location.replace = 'http://host.docker.internal:8000/login';
    }
})

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
            reset(field_type, '/user/details', withCredentials);
        })
    }
    else {
        const initial_value = $(this).closest('.my_account_initial_value').text();
        $('.my_account_details_submit').on('click', () => {
            let changed_value = $(`input[name='my_account_details_edit_${field_type}']`).val();
            if (changed_value !== initial_value) {
                const data = {[field_type]: changed_value};
                axios.patch('/user/details/', {
                    data: data,
                    withCredentials: withCredentials
                })
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
const $ = require('jquery');
const axios = require('axios');
const {global} = require('../../config.js');
const {check_user} = require('./sens');
import {gen_func} from '../shared/shared_gen_func.js';

let user_state = [false, false]

$(() => {
    user_state = check_user();
    if (!user_state[0]) {
        // window.location.replace = 'http://host.docker.internal:8000/login';
        gen_func.redirect(`${global.ngrok_frontend_url}/login/`);
    }
    if (user_state[0] && user_state[1]) {
        gen_func.redirect(`${global.ngrok_frontend_url}/products/`);
    }
})

$('#signup_verif_select_submit, .signup_verify_resend_code').on('click', (e) => {
    let method = $('input[name=signup_verif_select_option]').filter(':checked').val();
    data = {method: method};
    // axios.post('http://host.docker.internal:8000/verify_account/', {
    //     withCredentials: withCredentials,
    //     data: method
    // })
    axios.post(`${global.ngrok_api_url}/verify_account/`, method, global.options)
    .then((res) => {
        console.log(res);
        const message = res.data.message;
        if ($(e.target).hasClass('signup_verify_resend_code')) {
            $('.signup_verify_res_text_2').text(message);
        }
        else {
            $('.signup_verify_res_text_1').text(message);
            if (message === 'OTP has been sent!') {
                $('#signup_verif_select_cont').delay(1000).slideUp().$('#signup_verif_code_cont').slideDown();
            }
        }
    })
    .catch((error) => {
        console.log(error);
    })
});

$('#signup_verif_code_submit').on('click', () => {
    let user_otp = $('#signup_verify_code_input').val();
    user_otp = {user_input_otp: user_otp};
    axios.post(`${global.ngrok_api_url}/verify/otp/`, data, global.options)
    .then((res) => {
        console.log(res);
        const message = res.data.message;
        $('.signup_verify_res_text_2').text(message);
        if (message === 'VALID OTP!') {
            $('#signup_verif_code_cont').delay(1000).slideUp().$('#signup_details_cont').slideDown();
        }
    })
    .catch((err) => {
        console.log(err);
    })
});

$('#signup_details_submit').on('click', () => {
    if ($('#signup_details_company_check').is(':checked')) {
        $('.signup_details_company_details').slideDown();
    }
    else {
        $('.signup_details_company_details').slideUp();
    }
    data = {};
    $(`input[name='signup_details']`).each(() => {
        let val = $(this).val();
        if (val !== undefined || null) {
            let field = $(this).data('field-name');
            data.append(field, val);
        }
    })
    axios.post(`${global.ngrok_api_url}/user/details/`, data, global.options)
    .then((res) => {
        console.log(res);
    })
    .catch((err) => {
        console.log(err);
    })
});

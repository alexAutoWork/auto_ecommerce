const $ = require('jquery');
const axios = require('axios');

let is_logged_in = false;
let withCredentials = false;

$(() => {
    [is_logged_in, withCredentials] = check_user();
    if (!is_logged_in) {
        window.location.replace = 'http://host.docker.internal:8000/login';
    }
})

$('#signup_verif_select_submit, .signup_verify_resend_code').on('click', (e) => {
    let method = $('input[name=signup_verif_select_option]').filter(':checked').val();
    method = {method: method};
    axios.post('http://host.docker.internal:8000/verify_account/', {
        withCredentials: withCredentials,
        data: method
    })
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
    axios.post('http://host.docker.internal:3000/verify_otp/', {
        withCredentials: withCredentials,
        data: data
    })
    .then((res) => {
        console.log(res);
        const message = res.data.message;
        $('.signup_verify_res_text_2').text(message);
        if (message === 'VALID OTP!') {
            // axios.get('http://host.docker.internal:8000/user/details/', {withCredentials: true})
            // .then((res) => {
            //     console.log(res);
            //     data = res.data;
                
            // })
            // .catch((err) => {
            //     console.log(err);
            // })
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
    axios.post('http://host.docker.internal:3000/user/details/', {
        withCredentials: withCredentials,
        data: data
    })
    .then((res) => {
        console.log(res);
    })
    .catch((err) => {
        console.log(err);
    })
});

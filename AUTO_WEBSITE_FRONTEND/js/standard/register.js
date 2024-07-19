const $ = require('jquery');
const axios = require('axios');
const {global} = require('../../config');

$('#signup_email_pw_mobile_input_submit').on('click', () => {
    console.log('clicked!!!');
    let email = $('#signup_email_input').val();
    let password = $('#signup_pw_input').val();
    let mobile_no = $('#signup_mobile_input').val();
    let user_data = {email: email, password: password, mobile_no: mobile_no};
    console.log(user_data);
    axios.post(`${global.ngrok_api_url}/register/`, data, global.options)
    .then((res) => {
        console.log(res);
        const message = res.data.message;
        $('.signup_res_text_1').text(message);
        if (message === 'ACCOUNT CREATED!') {
            $('.signup_res_login_link').text(`<a href='${global.ngrok_frontend_url}/login'>click to login!</a>`);
        }
    })
    .catch((error) => {
        console.log(error.res.data);
    });
});
const $ = require('jquery');
const axios = require('axios');

$('#signup_email_pw_mobile_input_submit').on('click', () => {
    console.log('clicked!!!');
    let email = $('#signup_email_input').val();
    let password = $('#signup_pw_input').val();
    let mobile_no = $('#signup_mobile_input').val();
    let user_data = {email: email, password: password, mobile_no: mobile_no};
    console.log(user_data);
    axios.post('http://host.docker.internal:3000/register', {
        data: user_data
    })
    .then((response) => {
        console.log(response);
        const message = response.data.message;
        $('.signup_res_text_1').text(message);
        if (message === 'ACCOUNT CREATED!') {
            $('.signup_res_login_link').text('<a href="http://host.docker.internal:8080/login">click to login!</a>')
        }
    })
    .catch((error) => {
        console.log(error.response.data);
    });
});
const $ = require('jquery');
const axios = require('axios');
const {check_user} = require('./sens');

$(() => {
    [is_logged_in] = check_user();
    if (is_logged_in) {
        window.location.replace = 'http://host.docker.internal:8000/products';
    }
})

$('.login_signup_btn').on('click', () => {
    console.log('clicked!!!');
    let username = $('#login_user_input').val();
    let password = $('#login_pw_input').val();
    if (username.indexOf('@')) {
        let data = {'email': username, 'password': password}
    }
    if (username.indexOf('+')) {
        data = {'mobile_no': username, 'password': password}
    }
    data = JSON.stringify(data);
    axios.post('http://host.docker.internal:3000/login', {
        data: data,
    })
    .then((response) => {
        console.log(response);
        const message = response.data.message;
        $('.login_res_text_1').text(message)
        let redirect_url;
        if (message === 'Verify your account before using our service!') {
            redirect_url = 'http://host.docker.internal:8000/verify';
        }
        if (message === 'Successfully logged in!') {
            redirect_url = 'http://host.docker.internal:8000/products';
            localStorage.setItem('is_logged_in', true);
        }
        window.location.replace = redirect_url;
    })
    .catch((error) => {
        console.log(error);
    })
});
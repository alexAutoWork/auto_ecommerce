const $ = require('jquery');
const axios = require('axios');
const {check_user} = require('./sens');
const {global} = require('../../config');
import {gen_func} from '../shared/shared_gen_func';

$(() => {
    [is_logged_in, is_verified] = check_user();
    if (is_logged_in && is_verified) {
        gen_func.redirect(`${global.ngrok_frontend_url}/products`);
    } else {
        if (is_logged_in && !is_verified) {
            gen_func.redirect(`${global.ngrok_frontend_url}/verify`);
        }
    }
});

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
    axios.post(`${global.ngrok_api_url}/login/`, data, global.options)
    .then((res) => {
        console.log(res);
        const message = res.data.message;
        $('.login_res_text_1').text(res)
        let redirect_url;
        if (message === 'Verify your account before using our service!') {
            redirect_url = `${global.ngrok_frontend_url}/verify`;
            localStorage.setItem('is_logged_in', true);
        }
        if (message === 'Successfully logged in!') {
            redirect_url = `${global.ngrok_frontend_url}/products`;
            localStorage.setItem('is_logged_in', true);
            localStorage.setItem('is_verified', true);
        }
        gen_func.redirect(redirect_url);
    })
    .catch((error) => {
        console.log(error);
    })
});
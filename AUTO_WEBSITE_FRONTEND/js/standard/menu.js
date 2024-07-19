const axios = require('axios');
const $ = require('jquery');
const {check_user} = require('./sens');
import {gen_func} from '../shared/shared_gen_func';
const {logout} = require('./logout');
const {global} = require('../../config.js');

let user_state = [false, false]

$(() => {
    user_state = check_user();
    const toggle = gen_func.render_user_state(user_state, {args_1: 'logout', args_2: 'verify', args_3: 'login'});
    $('#shop_options_toggle_login').prop('data-toggle', toggle).text(toggle);
})

$('#shop_options_toggle_login').on('click', () => {
    return gen_func.render_user_state(user_state, {
        funct_1: logout,
        funct_2: gen_func.redirect,
        args_2: `${global.ngrok_frontend_url}/verify`,
        funct_3: gen_func.redirect,
        args_3: `${global.ngrok_frontend_url}/login`
    })
    // const toggle = $(this).data('toggle');
    // if (toggle === 'login') {
    //     window.location.replace = 'http://host.docker.internal:8000/login';
    // }
    // if (toggle === 'logout') {
    //     logout(withCredentials);
    // }
})
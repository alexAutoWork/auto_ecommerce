const axios = require('axios');
const $ = require('jquery');
const {check_user} = require('./sens');
const {logout} = require('./logout');

let is_logged_in = false;
let withCredentials = false;

$(() => {
    [is_logged_in, withCredentials] = check_user();
    let toggle;
    if (is_logged_in) {
        toggle = 'logout';
    }
    else {
        toggle = 'login';
    }
    $('#shop_options_toggle_login').prop('data-toggle', toggle).text(toggle);
})

$('#shop_options_toggle_login').on('click', () => {
    const toggle = $(this).data('toggle');
    if (toggle === 'login') {
        window.location.replace = 'http://host.docker.internal:8000/login';
    }
    if (toggle === 'logout') {
        logout(withCredentials);
    }
})
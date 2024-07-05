const $ = require('jquery');
const axios = require('axios');
const { token, user_id } = require('./sens.js');
const {load_bulk, page_main_load} = require('./my_account_global_items.js');
const {return_auth_page} = require('../shared/shared_gen_func');
const {check_user} = require('./sens');

let is_logged_in = false;
let withCredentials = false;

$(function() {
    [is_logged_in, withCredentials] = check_user();
    return_auth_page(is_logged_in);
})

function get_orders() {
    load_bulk('return');
}

function get_orders_page(order_id) {
    const axios_url = `http://host.docker.internal:3000/auth/orders/${order_id}`;
    axios.get(axios_url, {withCredentials: withCredentials})
    .then((res) => {
        data = res.data;
        page_main_load(data, 'order');
    })
    .catch((err) => {
        console.log(err);
    })
}
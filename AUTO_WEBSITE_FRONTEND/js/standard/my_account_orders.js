const $ = require('jquery');
const axios = require('axios');
const {load_bulk, page_main_load} = require('./my_account_global_items.js');
import {gen_func} from '../shared/shared_gen_func';
const {check_user} = require('./sens');
const {global} = require('../../config.js');

let user_state = [false, false]

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: get_orders, render_2: get_orders_page});
})

function get_orders() {
    load_bulk('order');
}

function get_orders_page(order_id) {
    const axios_url = `${global.ngrok_api_url}/auth/orders/${order_id}`;
    axios.get(axios_url, global.options)
    .then((res) => {
        data = res.data;
        page_main_load(data, 'order');
    })
    .catch((err) => {
        console.log(err);
    })
}
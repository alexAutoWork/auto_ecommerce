const $ = require('jquery');
const axios = require('axios');
const { return_page } = require('../shared/shared_functions.js');
const { global_load_tables } = require('./global_admin.js');

$(function() {
    return_page('order');
});

function get_orders() {
    global_load_tables('orders', ['orders_table']);
}
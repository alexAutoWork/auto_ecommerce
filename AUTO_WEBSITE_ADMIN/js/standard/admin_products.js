const $ = require('jquery');
const axios = require('axios');
const { return_page } = require('../shared/shared_functions.js');
const { global_load_tables, load_tables } = require('./global_admin.js');

$(function() {
    return_page();
})

function get_products() {
    global_load_tables('products', ['products_table', 'models_table', 'stocks_table']);
}

function get_product_page(id) {
    url = `http://host.docker.internal:3000/admin/products/${id}/`
    axios.get(url)
    .then((response) => {
        load_tables(response.data, [])
    })
}

function get_stock_page(id) {
    //
}

function get_model_page(id) {
    //
}
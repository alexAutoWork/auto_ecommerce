const $ = require('jquery');
const axios = require('axios');
const { token, user_id } = require('./sens.js');
const {load_bulk, page_main_load} = require('./my_account_global_items.js');
const {return_auth_page} = require('../shared/shared_gen_func');

let is_logged_in = false;
let withCredentials = false;

$(function() {
    [is_logged_in, withCredentials] = check_user();
    return_auth_page(is_logged_in);
})

function get_repairs() {
    load_bulk('repair');
}

function get_repairs_page(repair_id) {
    const axios_url = `http://host.docker.internal:3000/auth/repairs/${repair_id}`
    axios.get(axios_url, {withCredentials: withCredentials})
    .then((res) => {
        data = res.data;
        page_main_load(data, 'repair');
        $('.my_account_main_indi_item_repair_reason').text(data.reason_repair);
        $('.my_account_main_indi_item_error_codes').text(data.error_codes);
    })
    .catch((err) => {
        console.log(err);
    })
}
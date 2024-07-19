const $ = require('jquery');
const axios = require('axios');
const {check_user} = require('./sens');
const {load_bulk, page_main_load} = require('./my_account_global_items');
import {gen_func} from '../shared/shared_gen_func';
const {global} = require('../../config');

let user_state = [false, false]

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: get_repairs, render_2: get_repairs_page});
})

function get_repairs() {
    load_bulk('repair');
}

function get_repairs_page(repair_id) {
    const axios_url = `${global.ngrok_api_url}/auth/repairs/${repair_id}`
    axios.get(axios_url, global.options)
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
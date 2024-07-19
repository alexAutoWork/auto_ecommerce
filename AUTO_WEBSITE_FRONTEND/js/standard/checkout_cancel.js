const axios = require('axios');
const $ = require('jquery');
const {url_id_check} = import('../shared/shared_gen_func.mjs');
const {check_user} = require('./sens');
import {gen_func} from '../shared/shared_gen_func';
const {global} = require('../../config.js');

let user_state = [false, false]

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: main_load});
})

function main_load() {
    const url = url_id_check();
    const is_id = url[0];
    if (is_id) {
        const type = url[1];
        const id = url[2];
        $('.main').append(`<p class="message">if you still choose to proceed with your payment, your ${type} will still be saved...</p>`)
        const axios_url = `${global.ngrok_api_url}/auth/${id}/cancel/`;
        axios.get(axios_url, global.options)
        .then(() => {
            console.log('success!');
        })
        .catch((err) => {
            console.log(err);
        })
    }
}
const axios = require('axios');
const $ = require('jquery');
import {gen_func} from '../../node_modules/shared/shared_gen_func';
const {filter_on_change} = require('./filter_sort_methods.js');
const {product_func} = require('./products.js');
const {global} = require('../../config.js');

$(() => {
    axios.get(`${global.ngrok_api_url}/cities/`, global.options)
    .then((res) => {
        console.log(res);
        const cities = res.data;
        const cont = '.shop_options_location_select';
        const cont_mobi = '.shop_options_location_select_mobi';
        $(cont).empty();
        $(cont_mobi).empty();
        for (let city of cities) {
            let city_id = city.city_id;
            let city_value = city.city_value;
            $(`<button type="button" class="btn shop_options_location_option shop_options_location_option_btn global_font_3 global_remove_shadow" value="${city_id}">${city_value}</button>`).appendTo(cont);
            $(`<button type="button" class="btn shop_options_location_option_mobi shop_options_location_option_btn global_font_3 global_remove_shadow" value="${city_id}">${city_value}</button>`).appendTo(cont_mobi);
        }
    })
    .catch((err) => {
        console.log(err);
    })
});

function change_on_selection(e) {
    $('.shop_options_location_option_btn').not(this).removeClass('active');
    $(this).addClass('active');
    let city_id = $(this).val();
    const url = gen_func.url_id_check();
    const is_id = url[0];
    if (is_id) {
        const id = url[2]
        let axios_url = `${global.ngrok_api_url}/products/${id}/get_shipping_rate_on_change?city_id=${city_id}`;
        axios.get(axios_url, global.options)
        .then((res) => {
            data = res.data;
            product_func.render_shipping(data.base_charge, data.city_value);
        })
        .catch((err) => {
            console.log(err);
        })
    }
    else {
        filter_on_change(e);
    }
}

$(document).on('click', '.shop_options_location_option_btn', change_on_selection)
const axios = require('axios');
const $ = require('jquery');
import {render_func} from '../shared/shared_render_func';
import {gen_func} from '../shared/shared_gen_func';
const {check_user} = require('./sens');
const {global} = require('../../config.js');

let user_state = [false, false]

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: main_load});
})

function main_load() {
    const url = gen_func.url_id_check();
    const is_url = url[0];
    if (is_url) {
        const type = url[1];
        const type_id = url[2];
        const axios_url = `${global.ngrok_api_url}/auth/checkout/${type_id}/render-conf`;
        axios.get(axios_url, global.options)
        .then((res) => {
            data = res.data;
            $('.conf_default_message_cont').hide();
            if (type === 'repair') {
                load_repair_items(data.product_id);
            }
            else {
                load_order_items(data.order_items);
            }
            load_details(data, type, type_id);
        })
        .catch((err) => {
            console.log(err);
        })
    }
}

function load_order_items(data) {
    let items = [];
    for (let item of data) {
        let sku_no = item.sku_no;
        let product_config_id = sku_no.product_config_id;
        let product_id = product_config_id.product_id;
        let variation_id = product_config_id.variation_id;
        let img_location = `/public/${product_id.product_img_thumb}`;
        let html = 
        `<div class="container order_conf_order_items_product_cont">\n
            <div class="d-flex flex-row order_conf_order_items_product_cont_flex">\n
                <div class="p-2 order_conf_order_items_product_img">\n
                    ${img_location}\n
                </div>\n
                <div class="p-2 order_conf_order_items_product_details">\n
                    <p class="global_font_3 order_conf_order_items_product_details_name">${product_id.name}</p>\n
                    <p class="global_font_4 global_font_italic order_conf_order_items_product_details_type">TYPE: ${variation_id.variation_value}</p>\n
                    <p class="global_font_4 global_font_italic order_conf_order_items_product_details_sku">SKU NO: ${sku_no}</p>\n
                    <p class="global_font_3 d-block d-sm-block d-md-none">R${item.order_item_excl}</p>\n
                </div>
                <div class="p-2 order_conf_order_items_product_price d-none d-sm-none d-md-block d-lg-block d-xl-block">\n
                    <p class="global_font_3">R${item.order_item_excl}</p>\n
                </div>\n
            </div>\n
        </div>\n
        <hr>\n`
        items.push(html);
    }
    $('.order_conf_order_items_cont').append(items);
}

function load_repair_items(data) {
    let img_location = `/public/${data.product_img_thumb}`;
    let html =
    `<div class="container repair_conf_repair_items_product_cont">\n
        <div class="row repair_conf_repair_items_product_cont_row">\n
            <div class="col-2 repair_conf_repair_items_product_img">\n
                ${img_location}\n
            </div>\n
            <div class="col repair_conf_repair_items_product_details">\n
                <p class="global_font_3 repair_conf_repair_items_product_details_name">${data.name}</p>\n
            </div>\n
        </div>\n
    </div>\n`
    repair_conf_repair_items_cont.append(html);
}

function load_details(data, type, type_id) {
    $('.conf_id').text(type_id);
    let details = get_prop_by_string(data, `${type}_details`);
    let prefix;
    let shipping_price;
    if (type === 'repair') {
        shipping_price = details.shipping_price_excl;
        prefix = 'shipping_price';
    }
    if (type === 'order') {
        shipping_price = details.shipping_price;
        $('.conf_summary_quantity').text(`${details.order_quantity} ITEMS`);
        $('.conf_summary_subtotal_excl').text(`R${details.order_subtotal_excl}`);
        $('.conf_summary_subtotal_incl').text(`R${details.order_subtotal_incl}`);
        prefix = 'order';
    }
    $('.conf_summary_shipping_price_excl').text(`R${shipping_price}`);
    let tax = get_prop_by_string(details, `${prefix}_tax`);
    let total = get_prop_by_string(details, `${prefix}_total`);
    $('.conf_summary_tax').text(`R${tax}`);
    $('.conf_summary_total').text(`R${total}`);
    load_shipping_details_ov(details);
}

function load_shipping_details_ov(data) {
    let shipping_method_id = data.shipping_method_value;
    $('.conf_delivery_method').text(`${shipping_method_id}`);
    if (shipping_method_id === 1) {
        let address_html = load_shipping_details(data.shipping_address_id);
        // const excluded = ['address_id', 'user_id', 'name', 'is_active', 'is_default'];
        // let address = [];
        // let excluded_values = [];
        // for (let [key, value] of Object.entries(data.shipping_address_id)) {
        //     if (value !== null) {
        //         if (excluded.some(i => key.includes(i))) {
        //             excluded_values.push(value);
        //         }
        //         else {
        //             address.push(`${value}<br>\n`);
        //         }
        //     }
        // }
        // let name = excluded_values[2];
        // address = address.toString();
        // let address_html = 
        // `<p class="global_font_4 global_font_italic">${name}</p>\n
        // <p class="global_font_4 global_font_italic">${address}</p>\n`;
        $('.conf_address_cont').append(address_html);
    }
}
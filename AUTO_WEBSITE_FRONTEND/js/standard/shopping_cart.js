const $ = require('jquery');
const axios = require('axios');
const {check_user} = require('./sens');
import {gen_func} from '../shared/ES/shared_gen_func.js';
const {global} = require('../../config');

const is_full = gen_func.url_check('shopping-cart');

let user_state = [false, false];

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: main_load});
});

function main_load() {
    axios.get(`${global.ngrok_api_url}/cart/`, global.options)
    .then((res) => {
        const shopping_cart = res.shopping_cart;
        const shopping_cart_items = res.shopping_cart_items;
        is_full_html_load(shopping_cart, shopping_cart_items, {empty: true});
    })
    .catch((error) => {
        console.log(error);
    })
}

function quantity_text(total_quantity) {
    let total_quantity_text;
    if (total_quantity === 1) {
        total_quantity_text = `${total_quantity} ITEM`;
    }
    if (total_quantity > 1) {
        total_quantity_text = `${total_quantity} ITEMS`;
    }
    else {
        total_quantity_text = 'NO ITEMS';
    }
    return total_quantity_text
}

function get_conts() {
    if (typeof is_full === 'undefined') {
        const is_full = gen_func.url_check('shopping-cart');
    }
    if (is_full) {
        cont = '.shopping_cart_product_cont';
        cont_prefix = '.shopping_cart';
    }
    else {
        cont = '.shopping_cart_product_cont_mini';
        cont_prefix = '.shop_options_cart';
    }
    return {cont: cont, cont_prefix: cont_prefix}
}

function html_items_global(data, cont_prefix, $object) {
    $object.find(`${cont_prefix}_product_global`).each(() => {
        let field_value = $(this).data('insert-values');
        if (field_value === 'quantity' && $(this).data('is-selection')) {
            $(this).find('option:selected').prop('selected', false);
            $(this).find(`option[value='${data.quantity}']`).prop('selected', true);
        }
        else {
            let value = gen_func.get_prop(data, field_value);
            $(this).text(value);
        }
    });
}

function html_items(data, empty=false) {
    const conts = get_conts();
    const cont = conts.cont;
    const cont_prefix = conts.cont_prefix;
    const html = $(cont).first().clone();
    if (empty === true) {
        $(cont).empty();
    }
    for (let item of data) {
        let img_location = `/public/${item.product_img_thumb}`;
        html.data('shopping-cart-item-id', item.shopping_cart_item_id);
        html.data('product-config-id', item.product_config_id.product_config_id);
        html.find(`${cont_prefix}_product_img`).text(`<img src="${img_location}">`);
        html_items_global(item, cont_prefix, html);
        html.show();
        let output = `${html}\n<hr />`;
        $(output).appendTo(cont);
    }
    $(cont).find('hr').last().remove();
}

function mini_html(data) {
    $('.shop_options_cart_total').text(`TOTAL: ${data.total}`);
}

function main_html(data) {
    const total_quantity = data.total_quantity;
    const total_quantity_text = quantity_text(total_quantity);
    $('#shopping_cart_summary_qty').text(total_quantity_text);
    $('#shopping_cart_summary_subtotal').text(`R${data.subtotal}`);
    $('#shopping_cart_summary_vat').text(`R${data.vat}`);
    $('#shopping_cart_summary_total').text(`R${data.total}`);
}

function load_mini_checkout(shopping_cart, shopping_cart_items) {
    mini_html(shopping_cart)
    $('#shopping_cart_product_cont_all').empty();
    let shopping_cart_item_array = [];
    for (let item of shopping_cart_items) {
        let main_html = mini_html_items(item);
        shopping_cart_item_array.push(main_html);
    }
    $('.shop_options_cart_products').append(shopping_cart_item_array);
    $('hr').last().remove();
}

function load_full_checkout(shopping_cart, shopping_cart_items) {
    $('#shopping_cart_product_cont_all').empty();
    let shopping_cart_item_array = [];
    for (let item of shopping_cart_items) {
        let main_html = main_html_items(item);
        shopping_cart_item_array.push(main_html);
    }
    $('#shopping_cart_product_cont_all').append(shopping_cart_item_array);
    $('hr').last().remove();
    main_html(shopping_cart);
}

function html_loader(main_funct, data, opts=null, data_items=null) {
    let empty = false;
    if (typeof opts.empty !== 'undefined') {
        empty = true
    }
    main_funct(data);
    if (data_items !== null) {
        html_items(data_items, empty)
    }
}

function is_full_html_load(data, data_items=null, opts=null) {
    let main_funct;
    if (typeof is_full === 'undefined') {
        const is_full = gen_func.url_check('shopping-cart');
    }
    if (is_full) {
        main_funct = main_html;
    }
    else {
        main_funct = mini_html;
    }
    html_loader(main_funct, opts, data, data_items);
}

function add_cart_item(data) {
    axios.post(`${global.ngrok_api_url}/cart/`, data, global.options)
    .then((res) => {
        const data = res.data;
        const flag = data.flag;
        if (typeof flag !== 'undefined' && flag === 'updated') {
            inner_update_item(data);
        }
        else {
            is_full_html_load(data.shopping_cart, data.shopping_cart_items);
        }
    })
    .catch((err) => {
        console.log(err);
    })
}

function remove_cart_item(e) {
    const shopping_cart_item_id = $(this).parents().eq(5).data('shopping-cart-item-id');
    axios.delete(`${global.ngrok_api_url}/cart/${shopping_cart_item_id}/`, global.options)
    .then((res) => {
        const data = res.data;
        is_full_html_load(data.shopping_cart);
        $(this).remove();
    })
    .catch((err) => {
        console.log(err);
    })
}

function inner_update_item(data) {
    is_full_html_load(data.shopping_cart);
    const conts = get_conts();
    const cont_prefix = conts.cont_prefix;
    $object = $(conts.cont).find(`[data-shopping-cart-item-id='${shopping_cart_item_id}']`);
    html_items_global(data.shopping_cart_items, cont_prefix, $object);
}

function update_item(data) {
    shopping_cart_item_id = data.shopping_cart_item_id;
    delete data.shopping_cart_item_id;
    axios.patch(`${global.ngrok_api_url}/cart/${shopping_cart_item_id}/`, global.options)
    .then((res) => {
        const res_data = res.data;
        inner_update_item(res_data);
    })
    .catch((err) => {
        console.log(err);
    })
}

function change_on_quantity(e) {
    const quantity = $(this).find('option:selected').val();
    const shopping_cart_item_id = $(this).parents().eq(5).data('shopping-cart-item-id');
    const data = {
        quantity: quantity,
        shopping_cart_item_id: shopping_cart_item_id
    }
    update_item(data);
}

$(document).on('change', '.shopping_cart_product_qty_select', change_on_quantity)

$(document).on('change', '.shopping_cart_product_remove_btn, shop_options_cart_product_remove_btn', remove_cart_item)

export {add_cart_item, remove_cart_item, update_item}
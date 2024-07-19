const $ = require('jquery');
const axios = require('axios');
const {check_user} = require('./sens');
import {gen_func} from '../shared/shared_gen_func';
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
        const shopping_cart_details = res.data[0];
        const shopping_cart_item_details = res.data[1];
        if (is_full) {
            load_full_checkout(shopping_cart_details, shopping_cart_item_details);
        }
        else {
            load_mini_checkout(shopping_cart_details, shopping_cart_item_details);
        }
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

function html_items(data, cont, cont_prefix) {
    let img_location = `/public/${data.product_img_thumb}`;
    let html = $(cont).first().clone();
    html.data('shopping_cart_item_id', data.shopping_cart_item_id);
    html.data('product_config_id', data.product_config_id.product_config_id);
    html.find(`${cont_prefix}_product_img`).text(`<img src="${img_location}">`);
    html.find(`${cont_prefix}_product_global`).each(() => {
        let field_value = $(this).data('insert-values');
        let value = gen_func.get_prop(data, field_value);
        $(this).text(value);
    });
    html.show();
    html = `${html}\n<hr />`;
    return html
}

function mini_html_items(data) {
    return html_items(data, '.shopping_cart_product_cont_mini', '.shop_options_cart')
}

function main_html_items(data) {
    return html_items(data, '.shopping_cart_product_cont', '.shopping_cart')
}

function mini_html(data) {
    $('.shop_options_cart_total').text(`TOTAL: ${data.total}`);
}

function main_html(data) {
    const total_quantity = data.total_quantity;
    const total_quantity_text = quantity_text(total_quantity);
    $('#shopping_cart_summary_qty').text(total_quantity_text);
    $('#shopping_cart_summary_subtotal').text(`R${shopping_cart.subtotal}`);
    $('#shopping_cart_summary_vat').text(`R${shopping_cart.vat}`);
    $('#shopping_cart_summary_total').text(`R${shopping_cart.total}`);
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

function html_loader(data, data_items=null, functs) {
    const main_funct = functs.main_funct;
    const items_funct = functs.items_funct;
    const html_main = main_funct(data);
    let html_array = [html_main];
    let html_items = [];
    if (data_items !== null) {
        for (let item of data_items) {
            html_items.push(items_funct(data_items))
        }
    }

}

function is_full_html_load(data, data_items=null) {
    let main_html;
    let main_html_item;
    let html_array = [main_html];
    if (typeof is_full === 'undefined') {
        const is_full = gen_func.url_check('shopping-cart');
    }
    if (is_full) {
        main_html = main_html(data);
        if (data_items !== null) {
            for (let item of data_items) {
                main_html_item = main_html_items(item);
                html_array.push(main_html_item);
            }
        }
    }
    else {
        main_html = mini_html(data);
        if (data_items !== null) {
            for (let item of data_items) {
                main_html_item = mini_html_items(item);
                html_array.push(main_html_item);
            }
        }
    }
    return html_array
}

function add_cart_item(data) {
    axios.post(`${global.ngrok_api_url}/cart/`, data, global.options)
    .then((res) => {
        const data = res.data;
        let cart_item = is_full_html_load(data.shopping_cart_data, data.shopping_cart_item_data);
        $('#shopping_cart_product_cont_all').empty().append(cart_item[1]).find('hr').last().remove();
    })
    .catch((err) => {
        console.log(err);
    })
}

// function select_cart_item(shopping_cart_item_id) {
//     let item;
//     item = $('#shopping_cart_product_cont_all').children().attr(`[data-shopping-cart-item-id=${shopping_cart_item_id}]`)
//     if (item !== undefined || item !== 0 || item !== null) {
//         return item
//     }
//     else {
//         return False
//     }
// }

function remove_cart_item(shopping_cart_item_id, $object) {
    axios.delete(`${global.ngrok_api_url}/cart/${shopping_cart_item_id}/`, global.options)
    .then((res) => {
        const data = res.data;
        let shopping_cart_data = data.shopping_cart_data;
        is_full_html_load(shopping_cart_data);
        $($object).remove();
        $($object).parent().find('hr').last().remove();
    })
    .catch((err) => {
        console.log(err);
    })
}

function update_item(data, $object) {
    shopping_cart_item_id = data.shopping_cart_item_id;
    axios.patch(`${global.ngrok_api_url}/cart/${shopping_cart_item_id}/`, global.options)
    .then((response) => {
        const data = response.data;
        let shopping_cart_data = data.shopping_cart_data;
        let shopping_cart_item_data = data.shopping_cart_item_data;
        // let shopping_cart_item_id = shopping_cart_item_data.shopping_cart_item_id;
        // is_full_html_load();
        $($object).find('.shop_options_cart_product_price, .shopping_cart_product_price').text(`R${shopping_cart_item_data.total_price}`);
        $($object).find('.shop_options_cart_product_qty').text(`QTY: ${shopping_cart_item_data.quantity}`);
        $($object).find(`.shopping_cart_product_qty_select option[value="${shopping_cart_item_data.quantity}"]`).attr('selected', 'selected');
    })
    .catch((err) => {
        console.log(err);
    })
}

export {add_cart_item, remove_cart_item, update_item}
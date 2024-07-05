const $ = require('jquery');
const axios = require('axios');
const { url_check } = require('../shared/shared_functions.js');
const {check_user} = require('./sens');

const is_full = url_check('shopping-cart');

let is_logged_in = false;
let withCredentials = false;

$(() => {
    [is_logged_in, withCredentials] = check_user();
    if (is_logged_in) {
        axios.get('http://host.docker.internal:3000/cart/', {
            withCredentials: withCredentials
        })
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
    else {
        window.location.replace = 'http://host.docker.internal:8000/login';
    }
});

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

function mini_html_items(data) {
    let img_location = `/public/${data.product_img_thumb}`;
    let html = 
    `<div class="row shopping_cart_product_cont_mini" data-shopping-cart-item-id="${data.shopping_cart_item_id}">\n
        <div class="col-4">\n
            <img src="${img_location}">\n
        </div>\n
        <div class="col">\n
            <div class="container shop_options_cart_product_name_w_remove_cont">\n
                <div class="row">\n
                    <div class="col">\n
                        <p class="global_font_3 shop_options_cart_product_name">${data.product_name}</p>\n
                        <p class="global_font_4 shop_options_cart_product_type">type: ${data.variation_value}</p>\n
                    </div>\n
                    <div class="col-1">\n
                        <i class="fa-solid fa-trash shopping_cart_product_remove_btn"></i>\n
                    </div>\n
                </div>\n
            </div>\n
            <div class="container shop_options_cart_product_price_qty_cont">\n
                <div class="row">\n
                    <div class="col shop_options_cart_product_qty global_font_4">\n
                        QTY: ${data.quantity}\n
                    </div>\n
                    <div class="col shop_options_cart_product_price global_font_3">\n
                        R${data.total_price}\n
                    </div>\n
                </div>\n
            </div>\n
        </div>\n
    </div>\n\n
    <hr />`;
    return html
}

function main_html_items(data) {
    let img_location = `/public/${data.product_img_thumb}`;
    let html = 
    `<div class="container shopping_cart_product_cont" data-shopping-cart-item-id="${data.shopping_cart_item_id}">\n
        <div class="row shopping_cart_product_cont_row">\n
            <div class="col-12 col-sm-12 col-md-2 col-lg-2 col-xl-2 shopping_cart_product_cont_cols">\n
            <img src="${img_location}">\n
            </div>\n
            <div class="col-12 col-sm-12 col-md-7 col-lg-7 col-xl-7 shopp ing_cart_product_cont_cols">\n
                <div class="d-flex flex-column">\n
                    <div class="p-2 shopping_cart_product_name_cont">\n
                        <h2 class="global_font_2 shopping_cart_product_name">${data.product_name}</h2>\n
                    </div>\n
                    <div class="p-2 shopping_cart_product_type_cont">\n
                        <p class="global_font_4 shopping_cart_product_type">TYPE: ${data.variation_value}</p>\n
                    </div>\n
                </div>\n
            </div>\n
            <div class="col-12 col-sm-12 col-md-3 col-lg-3 col-xl-3 global_font_3 shopping_cart_product_price_qty_remove_cont shopping_cart_product_cont_cols">\n
                <div class="d-flex shopping_cart_product_price_qty_remove flex-row flex-sm-row flex-md-column flex-wrap flex-sm-wrap flex-md-nowrap">\n
                    <div class="p-2 shopping_cart_product_price_cont global_font_2">\n
                        <h2 class="shopping_cart_product_price">R${data.total_price}</h2>\n
                    </div>\n
                    <div class="p-2 shopping_cart_product_qty_select_cont">\n
                        <select class="form-control position-static custom-select global_qty_select_1 global_remove_shadow shopping_cart_product_qty_select">\n
                        <option>1</option>\n
                        <option>2</option>\n
                        <option>3</option>\n
                        <option>4</option>\n
                        <option>5</option>\n
                        </select>\n
                    </div>\n
                    <div class="p-2 shopping_cart_product_remove_cont align-self-center align-self-sm-center align-self-md-end align-self-lg-end align-self-xl-end">\n
                        <button type="button" class="btn global_remove_shadow global_font_3 global_black_icon_btn global_mobi_font_1 shopping_cart_product_remove_btn">REMOVE <i class="fa-solid fa-trash fa-lg d-none d-sm-block"></i><i class="fa-solid fa-trash d-block d-sm-none"></i></button>\n
                    </div>\n
                </div>\n
            </div>\n
        </div>\n
    </div>\n\n
    <hr />`;
    return html
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
    let shopping_cart_item_array = []
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

function is_full_html_load(data, data_items=null) {
    let main_html;
    let main_html_item;
    let html_array = [main_html];
    if (is_full) {
        main_html = main_html(data);
        if (data_items !== null) {
            main_html_item = main_html_items(data_items);
            html_array.push(main_html_item);
        }
    }
    else {
        main_html = mini_html(data);
        if (data_items !== null) {
            main_html_item = mini_html_items(data_items);
            html_array.push(main_html_item);
        }
    }
    return html_array
}

function add_cart_item(data) {
    axios.post('http://host.docker.internal:3000/cart/', {
        withCredentials: withCredentials,
        data: data,
    })
    .then((response) => {
        const data = response.data;
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
    axios.delete(`http://host.docker.internal:3000/cart/${shopping_cart_item_id}`, {withCredentials: true})
    .then((response) => {
        const data = response.data;
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
    axios.patch(`http://host.docker.internal:3000/cart/${shopping_cart_item_id}`, {withCredentials: true})
    .then((response) => {
        const data = response.data;
        let shopping_cart_data = data.shopping_cart_data;
        let shopping_cart_item_data = data.shopping_cart_item_data;
        // let shopping_cart_item_id = shopping_cart_item_data.shopping_cart_item_id;
        is_full_html_load( );
        $($object).find('.shop_options_cart_product_price, .shopping_cart_product_price').text(`R${shopping_cart_item_data.total_price}`);
        $($object).find('.shop_options_cart_product_qty').text(`QTY: ${shopping_cart_item_data.quantity}`);
        $($object).find(`.shopping_cart_product_qty_select option[value="${shopping_cart_item_data.quantity}"]`).attr('selected', 'selected');
        // let shopping_cart_item = select_cart_item(shopping_cart_item_id);
        // if (shopping_cart_item !== false) {
        //     shopping_cart_item.find('.shop_options_cart_product_price, .shopping_cart_product_price').text(`R${shopping_cart_item_data.total_price}`);
        //     shopping_cart_item.find('.shop_options_cart_product_qty').text(`QTY: ${shopping_cart_item_data.quantity}`);
        //     shopping_cart_item.find(`.shopping_cart_product_qty_select option[value="${shopping_cart_item_data.quantity}"]`);
        // }
        // else {
        //     throw new RangeError('shopping cart item not found');
        // }
    })
    .catch((err) => {
        console.log(err);
    })
}
const axios = require('axios');
const $ = require('jquery');
import {gen_func} from '../shared/shared_gen_func';
const {check_user} = require('./sens');
const {global} = require('../../config.js');

let is_saved = false;
let module;
let id = null;
let params = null;

let user_state = [false, false];

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: main_load});
})

function main_load() {
    const url = gen_func.url_id_check(true)
    const is_id = url[0];
    module = url[1];
    let suffix = module;
    if (is_id) {
        id = url[2];
        suffix = suffix + `/${id}`;
        is_saved = true;
    }
    else {
        if (module === 'repair') {
            params = url[2];
            suffix = suffix + `/?${params}`;
        }
    }
    const axios_url = `${global.ngrok_api_url}/auth/checkout/${suffix}`;
    axios.get(axios_url, global.options)
    .then((res) => {
        const data = res.data;
        const checkout_total = data.checkout_total;
        const checkout_items = data.checkout_items;
        const user_addresses = data.user_addresses;
        const active_address = data.active_address.address_id;
        if (module_type === 'repair') {
            load_checkout_items(checkout_items, repair=true);
            load_exchange_units(data.checkout_contains_ex);
            const repair_saved = ['reason_repair', 'error_codes'];
            for (let repair_val of repair_saved) {
                const data_val = gen_func.get_prop(data, `saved_${repair_val}`);
                if (data_val !== null) {
                    $(`input[name='${repair_val}']`).val(data_val);
                }
            }
        }
        if (module_type === 'order') {
            load_checkout_items(checkout_items);
        }
        load_checkout_total(checkout_total);
        load_user_addresses(user_addresses, active_address);
    })
    .catch((err) => {
        console.log(err);
    })
}

function load_checkout_items(data, repair=false) {
    checkout_items_html_array = [];
    for (let item of data) {
        let img_location = `/public/${item.product_img_thumb}`;
        let inner_html;
        let data_attrs;
        if (repair) {
            inner_html = 
            `<div class="p-2">\n
                <h3 class="global_font_3 request_repair_item_name">MERCEDES-BENZ BASE MODULE</h3>\n
            </div>`
            data_attrs = `data-product-id="${item.product_id}"`
        }
        else {
            inner_html = 
            `<div class="p-2">\n
                <h3 class="global_font_3 checkout_items_for_delivery_product_name">${item.product_name}</h3>\n
                <p class="global_font_4 global_font_italic checkout_items_for_delivery_product_type">TYPE: ${item.variation_value}</p>\n
                <p class="global_font_4 global_font_italic checkout_items_for_delivery_product_qty">QTY: ${item.quantity}</p>\n
            </div>\n
            <div class="p-2">\n
                <h3 class="global_font_3 checkout_items_for_delivery_product_price">${item.total_price}</h3>\n
            </div>\n`
            data_attrs = `data-shopping-cart-item-id="${item.shopping_cart_item_id}" data-variation-id="${item.variation_id}" data-product-id="${item.product_id}"`
        }
        let html = `
        <div class="container checkout_items_for_delivery_indi_item_cont" ${data_attrs}>\n
            <div class="row">\n
                <div class="col-2">\n
                    <img src="${img_location}">\n
                </div>\n
                <div class="col">\n
                    <div class="d-flex flex-column">\n
                        ${inner_html}
                    </div>\n
                </div>\n
            </div>\n
        </div>
        `
        checkout_items_html_array.push(html);
    }
    $('.checkout_items_cont').append(checkout_items_html_array);
}

function load_user_addresses(data, active_address_id) {
    let user_addresses_html_array = [];
    const excluded = ['address_id', 'user_id', 'name', 'is_active', 'is_default']
    for (let item of data) {
        let address = [];
        let excluded_values = [];
        let is_active = False;
        for (let [key, value] of Object.entries(item)) {
            if (value !== null) {
                if (excluded.some(i => key.includes(i))) {
                    excluded_values.push(value);
                }
                else {
                    if (active_address_id === data.address_id) {
                        is_active = true;
                    }
                    address.push(`${value}<br>\n`);
                }
            }
        }
        let address_id = excluded_values[0];
        let name = excluded_values[2];
        address = address.toString();
        let inner_address_html = 
        `<p>${name}</p>\n
        <p>${address}</p>`;
        let address_html_class = 'container global_font_3 checkout_delivery_address_indi_item';
        if (is_active) {
            address_html_class = address_html_class + ' active';
            $('.checkout_delivery_address').data('shipping-address-id', address_id).text(inner_address_html);
        }
        let address_html =
        `<div class="${address_html_class}" data-shipping-address-id="${address_id}">\n
            ${inner_address_html}\n
        </div>`;
        user_addresses_html_array.push(address_html);
    }
    $('#checkout_delivery_address_scroll_cont').append(user_addresses_html_array);
}

function load_checkout_total(data) {
    let summary = [];
    let excluded = ['total_quantity', 'subtotal_excl', 'total'];
    let excluded_values = [];
    for (let [key, value] of Object.entries(data)) {
        if (value !== null || 0) {
            if (excluded.some(i => key.includes(i))) {
                excluded_values.push(value);
            }
            else {
                if (key.includes('vat')) {
                    head = `${key} (15%)`;
                }
                else {
                    head = key;
                }
                let html_row = 
                `<tr class="checkout_summary_table_row">\n
                    <td class="checkout_summary_table_head">${head}</td>\n
                    <td class="checkout_summary_table_data" id="checkout_summary_shipping">R${value}</td>\n
                </tr>\n`;
                summary.push(html_row);
            }
        }
    }
    let total;
    let extra_html;
    if (excluded_values.length === 3) {
        extra_html = 
        `<tr class="checkout_summary_table_row">\n
            <td class="checkout_summary_table_head">${excluded_values[0]} ITEMS</td>\n
            <td class="checkout_summary_table_data" id="checkout_summary_shipping">R${excluded_values[1]}</td>\n
        </tr>\n`;
        total = excluded_values[2];
    }
    else {
        extra_html = '';
        total = excluded_values[0];
    }
    summary = summary.toString();
    let html = 
    `${extra_html}${summary}
    <tr class="checkout_summary_table_row">\n
        <td class="checkout_summary_table_blank"></td>\n
        <td class="checkout_summary_table_blank"></td>\n
    </tr>\n
    <tr class="checkout_summary_table_row">\n
        <td class="checkout_summary_table_head">TOTAL:</td>\n
        <td class="checkout_summary_table_data checkout_summary_table_total_data" id="checkout_summary_total">R${total}</td>\n
    </tr>`;
    $('table.checkout_summary_table > tbody').append(html);
}

function load_exchange_units(data) {
    if (data === true) {
        $('.checkout_exchange_unit_cont').show();
    }
}

function get_shipping_method(method_id, address_id=null) {
    data = {
        'shipping_method_id': method_id,
    }
    if (address_id !== null) {
        data.append('shipping_address_id', address_id)
    }
    const axios_url = `${global.ngrok_api_url}/auth/checkout/get_shipping_method/`;
    axios.post(axios_url, data, global.options)
    .then((res) => {
        load_checkout_total(res.data);
    })
    .catch((err) => {
        console.log(err);
    })
}

$('#checkout_exchange_unit_upload').on('change', () => {
    let form_data = new FormData();
    let file_data = $(this).prop('files')[0];
    let params = [
        {'user_type': 'user'},
        {'instance_type': 'order'},
    ]
    for (let param of params) {
        form_data.append(param);
    }
    form_data.append('file', file_data);
    axios.post(`${global.ngrok_api_url}/upload/`, form_data, global.options)
    .then((res) => {
        let status = res.status;
        if (status === 200) {
            let user_filename;
            let filename = res.data.filename;
            for (let [key, value] of form_data.entries()) {
                if (value instanceof File) {
                    user_filename = value.name;
                }
            }
            let html =
            `<p class="checkout_exchange_unit_photo_file_name global_font_italic" data-internal-filename="${filename}">${user_filename}<button type="button" class="btn global_remove_shadow global_black_icon_btn checkout_exchange_unit_photo_file_remove"><i class="fa-solid fa-trash fa-sm"></i></button></p>`
            $('.checkout_exchange_unit_photo_file_cont').append(html);
        }
    })
})

$('.checkout_exchange_unit_photo_file_remove').on('click', () => {
    let popup = '#checkout_exchange_unit_file_delete'
    let btn = '#checkout_change_delivery_address_cont'
    $(popup).modal('show');
    let file = $(this).parent();
    let internal_filename = file.data('internal-filename');
    $(`${btn}_submit`).on('click', () => {
        let axios_url = `${global.ngrok_api_url}/upload?filename=${internal_filename}`;
        axios.delete(axios_url, global.options)
        .then((res) => {
            if (res.status === 200) {
                file.hide();
            }
        })
        .catch((err) => {
            console.log(err);
        })
        $(popup).modal('hide');
    })
    $(`${btn}_close`).on('click', () => {
        $(popup).modal('hide');
    })
})

$('.checkout_delivery_method_btns').on('click', () => {
    let containers = ['checkout_delivery_address', 'checkout_pickup_address', 'checkout_courier_notice_cont']
    $('.checkout_delivery_method_btns').not(this).removeClass('active');
    $(this).addClass('active');
    let shipping_method_id = $(this).data('shipping_method_id');
    let shipping_address_id;
    let conts;
    if (shipping_method_id === 1) {
        conts = [containers[0]];
    }
    else {
        if (shipping_method_id === 2) {
            conts = [containers[1], containers[2]];
        }
        if (shipping_method_id === 3 || 4) {
            conts = [containers[3]];
        }
        shipping_address_id = null;
    }
    let cont = conts.join(', ');
    $(cont).show();
    for (let element of containers) {
        if ($(element).is(':visible')) {
            for (let item of conts) {
                if (element !== item) {
                    $(element).hide();
                }
            }
        }
    }
    get_shipping_method(shipping_method_id, shipping_address_id);
})

$('#checkout_delivery_address_change_popup').on('click', () => {
    const popup = '.checkout_delivery_address_change_popup'
    const item = '.checkout_delivery_address_indi_item'
    $(popup).modal('show');
    $(item).on('click', () => {
        $(item).not(this).removeClass('active');
        $(this).addClass('active');
    })
    $('#checkout_change_delivery_address_cont_submit').on('click', () => {
        let active_item = $(item).find('active');
        let shipping_address_id = $(active_item).data('shipping-address-id');
        let address = $(active_item).clone().find('div').remove();
        $('.checkout_delivery_address').text(address).data('shipping-address-id', shipping_address_id).trigger('get_shipping_method', [1, shipping_address_id]);
    })
    $('#checkout_change_delivery_address_cont_close').on('click', () => {
        $(popup).modal('show');
    })
})

$('#checkout_summary_payment_btn').on('click', () => {
    $('.checkout_payment_message').text('redirecting...');
    let data = {};
    if (module === 'order') {
        let exchange_unit = 'checkout_exchange_unit'
        let exchange_unit_cont = `${exchange_unit}_cont`;
        let filenames = [];
        if ((exchange_unit_cont).is(':visible')) {
            $(exchange_unit_cont).find(`${exchange_unit}_photo_file_cont`).children().each(() => {
                filenames.push($(this).data('internal-filename'));
            })
        }
        data.append('ex_unit_images', filenames);
    }
    if (module === 'repair') {
        let inputs = ['#checkout_repair_reason_input', '#checkout_repair_error_code_input']
        for (let input of inputs) {
            let val = $(input).val();
            let input_name = $(input).val();
            if (val !== undefined || null) {
                data.append(input_name, val);
            }
        }
    }
    let shipping_method_id = $('.checkout_delivery_method_btns').find('active').data('shipping_method_id');
    data.append('shipping_method_id', shipping_method_id);
    if (shipping_method_id === 1) {
        let shipping_address_id = $('.checkout_delivery_address').data('shipping-address-id')
        data.append('shipping_address_id', shipping_address_id);
    }
    if (is_saved) {
        const module_url = module + `/${id}`;
    }
    else {
        module_url = module;
    }
    let axios_url = `${global.ngrok_api_url}/auth/checkout/${module_url}/initialize/`;
    if (params !== null) {
        axios_url = axios_url + `?${params}`;
    }
    axios.post(axios_url, data, global.options)
    .then((res) => {
        if (res.status === 200) {
            window.location.replace('/checkout_redirect');
            let form_inputs_hidden = [];
            for (let [key, value] of Object.entries(res.data)) {
                html =
                `<input type="hidden" name="${key}" value="${value}">`
                form_inputs_hidden.push(html)
            }
            $('.checkout_payfast_form').append(form_inputs_hidden);
        }
    })
})


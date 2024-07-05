const $ = require('jquery');
const axios = require('axios');
const {load_shipping_details} = require('../shared/shared_render_func');
const {check_user} = require('./sens');

let is_logged_in = false;
let withCredentials = false;

$(() => {
    [is_logged_in, withCredentials] = check_user();
    if (is_logged_in) {
        $('.my_account_main_item_cont').remove();
        const url = `http://host.docker.internal:3000/user/addresses`;
        axios.get(url, {
            withCredentials: withCredentials
        })
        .then((res) => {
            const user_addresses = res.data;
            const excluded = ['address_id', 'user_id', 'name', 'is_active', 'is_default']
            for (let address of user_addresses) {
                let address_details = [];
                let excluded_values = [];
                for (let [key, value] of Object.entries(shipping_address_id)) {
                    if (value !== null) {
                        if (excluded.some(i => key.includes(i))) {
                            excluded_values.push(value);
                        }
                        else {
                            address_details.push(
                                `<span data-key="${key}">${value}</span>`
                            )
                        }
                    }
                }
                address_details = address_details.toString();
                const is_default = excluded_values[4];
                let is_default_html;
                let set_default_html;
                if (is_default == true) {
                    is_default_html = `<div class="p-2 ml-md-auto ml-lg-auto            ml-xl-auto">\n
                    <p class="global_font_4 global_font_italic">(DEFAULT)</p>\n
                    </div>\n`;
                    set_default_html = '<!-- SET DEFAULT: OPTION UNAVAILABLE -->';
                }
                else {
                    is_default_html = '<-- NOT DEFAULT -->'
                    set_default_html = `<div class="p-2 ml-md-auto ml-lg-auto ml-xl-auto my_account_address_book_set_default_btn_cont">\n
                        <button type="button" class="btn global_red_select_btn_2 global_remove_shadow my_account_address_book_set_default_btn">SET DEFAULT</button>\n
                    </div>\n`
                }
                let main_html = `
                <div class="container my_account_main_item_cont" data-address-id="${address_details[0]}">\n
                    <div class="row">\n
                        <div class="col-12 col-sm-12 col-md-8 col-lg-7 col-xl-7 global_font_4 my_account_main_item_address_details_cont">\n
                            <p class="global_font_4 global_font_italic" data-key="name">${excluded_values[2]}</p>
                            <p class="global_font_4 global_font_italic">${address_details}</p>
                        </div>\n
                        <div class="col">\n
                            <div class="d-flex flex-column my_account_main_item_btn_col">\n
                                ${is_default_html}
                                <div class="p-2 mt-md-auto ml-md-auto mt-lg-auto ml-lg-auto mt-xl-auto ml-xl-auto my_account_address_book_edit_delete_btn_cont">\n
                                    <div class="d-flex flex-row my_account_address_book_edit_delete_btn_cont_inner">\n
                                        <div class="p-2 my_account_address_book_delete_btn_cont">\n
                                            <button type="button" class="btn global_red_select_btn_2 global_remove_shadow my_account_address_book_delete_btn">DELETE</button>\n
                                        </div>\n
                                        <div class="p-2 my_account_address_book_edit_btn_cont">
                                            <button type="button" class="btn global_red_select_btn_2 global_remove_shadow my_account_address_book_edit_btn">EDIT</button>
                                        </div>\n
                                    </div>\n
                                </div>\n
                                ${set_default_html}
                            </div>\n
                        </div>\n
                    </div>\n
                </div>`;
                main_html.appendto('.my_account_address_book_cont');
            }
        })
    }
    else {
        window.location.replace = 'http://host.docker.internal:8000/login';
    }
});

$('.my_account_address_book_set_default_btn').on('click', () => {
    const address_id = $(this).closest('[data-address-id]');
    if (address_id !== undefined) {
        axios.patch(`http://host.docker.internal:3000/user/addresses/${address_id}/make_default`, {withCredentials: withCredentials})
        .then((res) => {
            location.reload();
        })
        .catch((err) => {
            console.log(err);
        })
    }
})

$('.my_account_address_book_edit_btn').on('click', () => {
    const address_id = $(this).closest('[data-address-id]');
    let address_details = {};
    let address_name = null;
    address_id.children('.my_account_main_item_address_details_cont').children('p').each((index) => {
        if (index === 0) {
            let data_attr = $(this).data('key');
            if (data_attr === 'name') {
                address_name = data_attr.text();
            }
        else {
            $(this).children('span').each(() => {
                let data_attr = $(this).data('key');
                address_details.append(data_attr, data_attr.text());
            })
        }
        }
    })
    const address_popup = $('.my_account_add_address_popup1');
    address_popup.find('.my_account_add_address_popup_header').text('EDIT ADDRESS');
    address_popup.modal('show');
    for (let [key, value] of Object.entries(address_details)) {
        address_popup.find(`[data-field-name="${key}"]`).val(value);
    }
    $('.my_account_add_address_input').on('click', () => {
        $(this).data('clicked', true);
    })
    $('#my_account_add_address_submit').on('click', () => {
        let data = {};
        $('my_account_add_address_input').each(() => {
            let is_clicked = $(this).data('clicked');
            if (is_clicked) {
                let key = $(this).data('field-name');
                data.append(key, key.val());
            }
        })
        axios.patch(`http://host.docker.internal:3000/user/addresses/${address_id}/`, {
            withCredentials: withCredentials,
            data: data
        })
        .then((res) => {
            console.log(res.data.message);
            location.reload();
        })
        .catch((err) => {
            console.log(err);
        })
    })
})

$('.my_account_address_book_add_address_btn').on('click', () => {
    const address_popup = $('.my_account_add_address_popup1');
    address_popup.modal('show');
    $('#my_account_add_address_submit').on('click', () => {
        let data = {};
        $('my_account_add_address_input').each(() => {
            let key = $(this).data('field-name');
            let val = key.val();
            if (data === undefined || null) {
                data.append(key, val);
            }
        })
        axios.post('http://host.docker.internal:3000/user/addresses/', {
            withCredentials: true,
            data: data
        })
        .then((res) => {
            console.log(res.data.message);
            location.reload();
        })
        .catch((err) => {
            console.log(err);
        })
    })
})
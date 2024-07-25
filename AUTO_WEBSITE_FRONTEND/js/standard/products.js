const axios = require('axios');
const $ = require('jquery');
// const { return_page } = import('../shared/shared_gen_func.mjs');
const {add_cart_item} = require('./shopping_cart.js');
import {gen_func} from '../shared/ES/shared_gen_func.js';
const { check_user } = require('../standard/sens.js');
const {global} = require('../../config.js');

function product_config_switch(variation_id) {
    switch (variation_id) {
        case 1:
            let product_config_button_name = 'Exchange Unit';
            let product_config_button_id = 'product_select_exchange_unit'
            return [product_config_button_name, product_config_button_id]
        case 2:
            product_config_button_name = 'Sale';
            product_config_button_id = 'product_select_sale'
            return [product_config_button_name, product_config_button_id]
        case 3:
            product_config_button_name = 'Second-Hand';
            product_config_button_id = 'product_select_second_hand';
            return [product_config_button_name, product_config_button_id]
        default:
            let product_config_message = 'Unavailable';
            console.log(product_config_message);
            break;
    }
};

function detect_amount_for_config_price(product_price) {
    let product_amount = $('#quantity_select option:selected').val();
    console.log(product_amount);
    console.log(Number(product_amount));
    let amount = product_price * product_amount;
    $('.product_price_2').text(`R${amount}`).data('cal-price', amount);
};

function product_select_btn_type(e) {
    console.log('clicked!!');
    $('.product_select_type').removeClass('active');
    $(this).addClass('active');
    let product_config_price = $(this).data('product-config-price');
    console.log(product_config_price);
    console.log(Number(product_config_price));
    detect_amount_for_config_price(product_config_price);
}

$(document).on('click', '.product_select_type', product_select_btn_type);

$('.product_price_qty_select').on('change', () => {
    let product_price = $('.product_select_type.active').data('product-config-price');
    console.log(product_price)
    detect_amount_for_config_price(product_price);
});

$('.product_add_to_cart').on('click', () => {
    let quantity = $('#quantity_select option:selected').val();
    let product_config_id = $('.product_select_type.active').data('product-config-id');
    const data = {
        quantity: quantity,
        product_config_id: product_config_id
    }
    add_cart_item(data);
})

const render_func = {
    render_shipping: function(rate, city_name=null) {
        if (rate !== null) {
            $('.product_shipping_city_name').text(city_name);
            $('.product_shipping_rate_inner').text(rate);
        } else {
            $('.shipping_rate_user_city').hide();
            $('.product_shipping_rate').hide();
        }
    },
    render_products: function(data) {
        const products = data;
        console.log(products);
        let product_html_array = [];
        for (let product of products) {
            let product_details = product.product;
            let product_id = product_details.product_id;
            let name = product_details.name;
            let brand = product_details.brand_id;
            let category = product_details.category_id;
            let img = product_details.product_img_thumb;
            let img_location = `/public/${img}`
            let shipping_rate_details = product.shipping_rate;
            let shipping_rate;
            if (shipping_rate_details !== undefined) {
                shipping_rate = shipping_rate_details.base_charge;
            }
            else {
                shipping_rate = ' ';
            }
            let html = `<div class="p-2" data-category-id="${category}" data-brand-id="${brand}" data-product-id="${product_id}" data-product-name="${name}">\n <div class="card product_item">\n <img class="card-img-top product_item_img" src="${img_location}">\n <div class="card-body product_item_body">\n <h2 class="product_item_header">${name}</h2>\n <p class="product_shipping_amount">${shipping_rate}</p>\n <a role="button" class="btn global_font_3 global_red_select_btn_2 product_item_view_btn global_remove_shadow" href="/products/${product_id}">VIEW</a>\n </div>\n <div>\n </div>`
            product_html_array.push(html);
        }
        $('.product_item_row').empty().append(product_html_array);
    }
}

const product_func = {
    ...render_func,
    get_products: function(kwargs=null) {
        let url = `${global.ngrok_api_url}/products/`;
        let query_param_list = [];
        query_param_list.length = 0;
        if (kwargs !== null) {
            for (const key of Object.keys(kwargs)) {
                let prop = gen_func.get_prop(kwargs, key);
                console.log(prop);
                if (Array.isArray(prop)) {
                    if (prop.length === 0) {
                        prop = null;
                    } else {
                        prop = prop.toString();
                    }
                }
                if (prop !== null) {
                    value = `${key}=${prop}`;
                    query_param_list.push(value);
                }
            }
        }
        if (query_param_list.length !== 0) {
            let query_params = query_param_list.join('&');
            url = `${url}?${query_params}`;
        }
        console.log(query_param_list);
        console.log(url);
        axios.get(url, global.options)
        .then((res) => {
            console.log(res);
            console.log(res.data);
            render_func.render_products(res.data);
        })
        .catch((error) => {
            console.log(error);
        })
    }
}

function get_products_page(product_id) {
    const product_url = `${global.ngrok_api_url}/products/${product_id}/`;
    axios.get(product_url, global.options)
    .then((response) => {
        const product_details_list = response.data;
        console.log(product_details_list);
        console.log(product_details_list.product_details);
        console.log(product_details_list.product_models);
        // product details
        const product_details = product_details_list.product_details;
        const product_id = product_details.product_id;
        const img = product_details.product_img;
        const img_url = `/public/${img}`;
        const img_html = `<img src="${img_url}" style="width: 100%;">`;
        $('.product_img_cont').empty().append(img_html);
        $('.product_name').text(product_details.name);
        $('#product_info_table_data_dimensions').text(`${product_details.dimension_w}cm(w) x ${product_details.dimension_l}cm(l) x ${product_details.dimension_h}cm(h)`);
        let weight_type = product_details.weight_type;
        if (weight_type === null) {
            weight_type = 'kg';
        }
        $('#product_info_table_data_weight').text(`${product_details.weight}${product_details.weight_type}`);
        $('#product_info_table_data_warranty').text(product_details.warranty);
        const is_repairable = product_details.is_repairable;
        let is_rep_html;
        if (is_repairable === true) {
            let is_rep_url = `${global.ngrok_frontend_url}/checkout/repair/${product_id}/`;
            is_rep_html = gen_func.render_user_state(user_state, {
                args_1: `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" href="${is_rep_url}">REQUEST A REPAIR</a></p>`,
                args_2: `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><span tabindex="0" data-toggle="popover" data-trigger="focus" data-placement="right" data-content="Please register before requesting a repair!"><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" style="pointer-events: none;" disabled>REQUEST A REPAIR</a></span></p>`,
                args_3: `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><span tabindex="0" data-toggle="popover" data-trigger="focus" data-placement="right" data-content="Please verify before requesting a repair!"><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" style="pointer-events: none;" disabled>REQUEST A REPAIR</a></span></p>`
            })
        }
        else {
            is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-xmark product_repairable_icon fa-lg"></i>`;
        }
        const product_shipping_rate = product_details_list.product_shipping_rate;
        product_func.render_shipping(product_shipping_rate.base_charge, product_shipping_rate.city_value);
        $('.product_repairable_cont').empty().append(is_rep_html);
        // product brand
        $('#product_info_table_data_brand').text(product_details.brand_id);
        // product category
        $('#product_info_table_data_category').text(product_details.category_id);
        // product models
        const product_models = product_details_list.product_models;
        let product_models_html_array = []
        for (let model of product_models) {
            let model_number = model.model_number;
            product_models_html_array.push(`<li>${model_number}</li>\n`);
        }
        $('#product_models_content').empty().append(product_models_html_array);
        const product_configs = product_details_list.product_prices;
        for (let product_config of product_configs) {
            let product_config_text = product_config.variation_id;
            let product_config_html = 
            `<button type="button" class="btn global_remove_shadow global_red_select_btn_1 global_mobi_font_1 product_select_type" data-product-config-id="${product_config.product_config_id}" data-product-config-price="${product_config.price}">${product_config_text}</button>`;
            // let product_config_html = 
            // `<button type="button" class="btn global_remove_shadow global_red_select_btn_1 global_mobi_font_1 product_select_type" id="product_select_${product_config_text.toLowerCase()}" data-product-config-id="${product_config.product_config_id}" data-product-config-price="${product_config.price}">${product_config_text}</button>`;
            $(product_config_html).appendTo('.product_selected_type_cont');
        }

    })
    .catch((error) => {
        console.log(error);
    })
};

$('.product_add_to_cart').on('click', () => {
    const product_config_id = $('.product_select_type.active').data('product-config-id');
    const quantity = $('#quantity_select option:selected').val();
    const data = {
        product_config_id: product_config_id,
        quantity: quantity
    };
    add_cart_item(data);
});

let user_state = [false, false]

$(() => {
    user_state = check_user();
    gen_func.render_page(get_products_page, product_func.get_products);
});

export {product_func}
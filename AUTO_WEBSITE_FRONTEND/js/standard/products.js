const axios = require('axios');
const $ = require('jquery');
// const { return_page } = import('../shared/shared_gen_func.mjs');
const {return_page} = require('../standard/test.js');
const { check_user } = require('../standard/sens.js');

function get_products(sort=null, brands=null, categories=null, city_id=null) {
    // let url = `http://localhost:3000/products`;
    // let url = `http://host.docker.internal:3000/products`;
    let url = `https://1f9f-102-68-28-61.ngrok-free.app/products/`;
    let query_param_list = []
    if (sort !== null) {
        let sort = `sort=${sort}`;
        query_param_list.push(sort);
    }
    if (brands !== null) {
        let brands = brands.toString();
        brands = `filter_brand=${brands}`;
        query_param_list.push(brands);
    }
    if (categories !== null) {
        let categories = categories.toString();
        categories = `filter_category=${categories}`;
        query_param_list.push(categories);
    }
    if (city_id !== null) {
        let city_id = `city_id=${city_id}`;
        query_param_list.push(city_id);
    }
    if (query_param_list.length !== 0) {
        let query_params = query_param_list.join('&');
        url = `${url}?${query_params}`;
    }
    axios.get(url, {
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    })
    .then((response) => {
        const products = response.data;
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
                shipping_rate = ' '
            }
            let html = `<div class="p-2" data-category-id="${category}" data-brand-id="${brand}" data-product-id="${product_id}" data-product-name="${name}">\n <div class="card product_item">\n <img class="card-img-top product_item_img" src="${img_location}">\n <div class="card-body product_item_body">\n <h2 class="product_item_header">${name}</h2>\n <p class="product_shipping_amount">${shipping_rate}</p>\n <a role="button" class="btn global_font_3 global_red_select_btn_2 product_item_view_btn global_remove_shadow" href="/products/${product_id}">VIEW</a>\n </div>\n <div>\n </div>`
            product_html_array.push(html);
        }
        $('.product_item_row').empty().append(product_html_array);
    })
    .catch((error) => {
        console.log(error);
    })
}

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

function get_products_page(product_id) {
    const product_url = `https://1f9f-102-68-28-61.ngrok-free.app/products/${product_id}/`;
    axios.get(product_url)
    .then((response) => {
        const product_details_list = response.data;
        console.log(product_details_list);
        console.log(product_details_list[0].product_details);
        console.log(product_details_list[1].product_models[0]);
        // product details
        const product_details = product_details_list[0].product_details;
        const product_id = product_details.product_id;
        const img = product_details.product_img;
        const img_url = `/public/${img}`;
        const img_html = `<img src="${img_url}" style="width: 100%;">`;
        $('.product_img_cont').empty().append(img_html);
        $('.product_name').text(product_details.name);
        $('#product_info_table_data_dimensions').text(`${product_details.dimension_w}cm(w) x ${product_details.dimension_l}cm(l) x ${product_details.dimension_h}cm(h)`);
        $('#product_info_table_data_weight').text(`${product_details.weight}${product_details.weight_type}`);
        $('#product_info_table_data_warranty').text(product_details.warranty);
        const is_repairable = product_details.is_repairable;
        let is_rep_html;
        if (is_repairable === true) {
            let is_rep_url = `http://host.docker.internal:8080/checkout/repair/${product_id}/`;
            if (is_logged_in === true) {
                is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" href="${is_rep_url}">REQUEST A REPAIR</a></p>`;
            }
            else {
                is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><span tabindex="0" data-toggle="popover" data-trigger="focus" data-placement="right" data-content="Please register before requesting a repair!"><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" style="pointer-events: none;" disabled>REQUEST A REPAIR</a></span></p>`;
            }
        }
        else {
            is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-xmark product_repairable_icon fa-lg"></i>`;
        }
        $('.product_repairable_cont').empty().append(is_rep_html);
        // product brand
        const product_brand = product_details_list[3].product_brand.brand_value;
        $('#product_info_table_data_brand').text(product_brand);
        // product category
        const product_category = product_details_list[4].product_category.category_value;
        $('#product_info_table_data_category').text(product_category);
        // product models
        const product_models = product_details_list[1].product_models
        let product_models_html_array = []
        for (let model of product_models) {
            let model_number = model.model_number;
            product_models_html_array.push(`<li>${model_number}</li>\n`);
        }
        $('#product_models_content').empty().append(product_models_html_array);
    })
    .catch((error) => {
        console.log(error);
    })
};

function detect_amount_for_config_price(product_price) {
    let product_amount = $('select[name="amount_option"]').val();
    let amount = product_price * product_amount;
    $('.product_price_2').text(`R${amount}`);
};

$('.product_select_type').on('click', () => {
    $('.product_select_type').removeClass('active');
    $(this).addClass('active');
    let product_config_price = $(this).attr('value');
    detect_amount_for_config_price(product_config_price);
});

$('.product_price_qty_select').on('change', () => {
    let product_price = $('.product_price_2').text();
    detect_amount_for_config_price(product_price);
});

let is_logged_in = false;
let withCredentials = false;

$(() => {
    [is_logged_in, withCredentials] = check_user();
    return_page(get_products_page, get_products);
});

exports.get_products = get_products
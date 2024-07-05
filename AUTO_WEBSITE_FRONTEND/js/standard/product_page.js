// const axios = require('axios');
// const $ = require('jquery');
// const { token } = require('./sens.js');


// function product_config_switch(variation_id) {
//     switch (variation_id) {
//         case 1:
//             let product_config_button_name = 'Exchange Unit';
//             let product_config_button_id = 'product_select_exchange_unit'
//             return [product_config_button_name, product_config_button_id]
//         case 2:
//             product_config_button_name = 'Sale';
//             product_config_button_id = 'product_select_sale'
//             return [product_config_button_name, product_config_button_id]
//         case 3:
//             product_config_button_name = 'Second-Hand';
//             product_config_button_id = 'product_select_second_hand';
//             return [product_config_button_name, product_config_button_id]
//         default:
//             let product_config_message = 'Unavailable';
//             console.log(product_config_message);
//             break;
//     }
// };

// $(function() {
//     const url = window.location.pathname;
//     const id = url.substring(url.lastIndexOf('/') + 1);
//     const product_url = `http://host.docker.internal:3000/products/${id}/`;
//     axios.get(product_url, {
//         headers: {'Content-Type': 'application/json'}})
//     .then((response) => {
//         const product_details_list = response.data;
//         console.log(product_details_list);
//         console.log(product_details_list[0].product_details);
//         console.log(product_details_list[1].product_models[0]);
        // product details
        // const product_details = product_details_list[0].product_details;
        // const product_id = product_details.product_id;
        // const img = product_details.product_img;
        // const img_url = `/public/${img}`;
        // const img_html = `<img src="${img_url}" style="width: 100%;">`;
        // $('.product_img_cont').empty().append(img_html);
        // $('.product_name').text(product_details.name);
        // $('#product_info_table_data_dimensions').text(`${product_details.dimension_w}cm(w) x ${product_details.dimension_l}cm(l) x ${product_details.dimension_h}cm(h)`);
        // $('#product_info_table_data_weight').text(`${product_details.weight}${product_details.weight_type}`);
        // $('#product_info_table_data_warranty').text(product_details.warranty);
        // const is_repairable = product_details.is_repairable;
        // let is_rep_html;
        // if (is_repairable === true) {
        //     let is_rep_url = `http://host.docker.internal:8080/repair/${product_id}/`;
        //     if (token != false) {
        //         is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" href="${is_rep_url}">REQUEST A REPAIR</a></p>`;
        //     }
        //     else {
        //         is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><span tabindex="0" data-toggle="popover" data-trigger="focus" data-placement="right" data-content="Please register before requesting a repair!"><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" style="pointer-events: none;" disabled>REQUEST A REPAIR</a></span></p>`;
        //     }
        // }
        // else {
        //     is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-xmark product_repairable_icon fa-lg"></i>`;
        // }
        // $('.product_repairable_cont').empty().append(is_rep_html);
        // product brand
        // const product_brand = product_details_list[3].product_brand.brand_value;
        // $('#product_info_table_data_brand').text(product_brand);
        // product category
        // const product_category = product_details_list[4].product_category.category_value;
        // $('#product_info_table_data_category').text(product_category);
        // product models
        // const product_models = product_details_list[1].product_models
        // let product_models_html_array = []
        // for (let model of product_models) {
        //     let model_number = model.model_number;
        //     product_models_html_array.push(`<li>${model_number}</li>\n`);
        // }
        // $('#product_models_content').empty().append(product_models_html_array);
        // for (let detail_item of product_details_list) {
        //     if (detail_item === 'product_details') {
        //         const product_details = detail_item.product_details;
        //         const product_id = product_details.product_id;
        //         const img = product_details.product_img;
        //         const img_url = `/public/${img}`;
        //         const img_html = `<img src="${img_url}" style="width: 100%;">`;
        //         $('.product_img_cont').empty().append(img_html);
        //         $('.product_name').text(product_details.name);
        //         $('#product_info_table_data_dimensions').text(`${product_details.dimension_w}cm(w) x ${product_details.dimension_l}cm(l) x ${product_details.dimension_h}cm(h)`);
        //         $('#product_info_table_data_weight').text(`${product_details.weight}${product_details.weight_type}`);
        //         $('#product_info_table_data_warranty').text(product_details.warranty);
        //         const is_repairable = product_details.is_repairable;
        //         let is_rep_html;
        //         if (is_repairable === true) {
        //             let is_rep_url = `http://host.docker.internal:8080/repair/${product_id}/`;
        //             if (token != false) {
        //                 is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" href="${is_rep_url}">REQUEST A REPAIR</a></p>`;
        //             }
        //             else {
        //                 is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-check product_repairable_icon fa-lg"></i><span tabindex="0" data-toggle="popover" data-trigger="focus" data-placement="right" data-content="Please register before requesting a repair!"><a role="button" class="btn global_remove_shadow global_black_select_btn_2 product_request_repair_btn global_mobi_font_1" style="pointer-events: none;" disabled>REQUEST A REPAIR</a></span></p>`;
        //             }
        //         }
        //         else {
        //             is_rep_html = `<p>REPAIRABLE:<i class="fa-solid fa-xmark product_repairable_icon fa-lg"></i>`;
        //         }
        //         $('.product_repairable_cont').empty().append(is_rep_html);
        //     }
        //     if (detail_item == detail_item.product_brand) {
        //         const brand = detail_item.product_brand.brand_value;
        //         $('#product_info_table_data_brand').text(brand);
        //     }
        //     if (detail_item == detail_item.product_category) {
        //         const category = detail_item.product_category.category_value;
        //         $('#product_info_table_data_category').text(category);
        //     }
        //     if (detail_item == detail_item.product_models) {
        //         const product_models = detail_item.product_models;
        //         let product_models_html_array = []
        //         for (let item of product_models) {
        //             let model_number = item.model_number;
        //             product_models_html_array.push(`<li>${model_number}</li>`);
        //         }
        //         $('#product_models_content').empty().append(product_models_html_array);
        //     }
        //     if (detail_item == detail_item.product_prices) {
        //         const product_prices = detail_item.product_prices;
        //         let product_prices_html_array = []
        //         for (let config of product_prices) {
        //             const variation_id = config.variation_id;
        //             let product_config_id = config.product_config_id;
        //             let product_config_price = config.price;
        //             let [product_config_button_name, product_config_button_id] = product_config_switch(variation_id);
        //             let product_config_html = `<button type="button" class="btn global_remove_shadow global_red_select_btn_1 global_mobi_font_1" id="${product_config_button_id}" data-product-config-id="${product_config_id}" value="${product_config_price}">${product_config_button_name}</button>`;
        //             product_prices_html_array.push(product_config_html);
        //         }
        //         $('.product_selected_type_cont').empty().append(product_prices_html_array);
        //     }
        //     if (detail_item == detail_item.product_shipping_rate) {
        //         const shipping_rate_user_city = detail_item.product_shipping_rate.city_value;
        //         const product_shipping_rate = detail_item.product_shipping_rate.base_charge;
        //         $('.shipping_rate_user_city').text(`<i class="fa-solid fa-location-dot"></i> Delivery to: ${shipping_rate_user_city}`);
        //         $('.product_shipping_rate').text(`SHIPPING COST: R${product_shipping_rate}`);
        //     }
        // }
//     })
//     .catch((error) => {
//         console.log(error);
//     })
// });

// function detect_amount_for_config_price(product_price) {
//     let product_amount = $('select[name="amount_option"]').val();
//     let amount = product_price * product_amount;
//     $('.product_price_2').text(`R${amount}`);
// };

// $('.product_select_type').on('click', function() {
//     $('.product_select_type').removeClass('active');
//     $(this).addClass('active');
//     let product_config_price = $(this).attr('value');
//     detect_amount_for_config_price(product_config_price);
// });

// $('.product_price_qty_select').on('change', function() {
//     let product_price = $('.product_price_2').text();
//     detect_amount_for_config_price(product_price);
// });
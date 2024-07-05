const axios = require('axios');
const $ = require('jquery');
const {filter_on_change} = require('./filter_sort_methods.js');

$(() => {
    axios.get('http://host.docker.internal:3000/cities')
    .then((res) => {
        console.log(res);
        const cities = res.data;
        for (let city of cities) {
            let city_id = city.city_id;
            let city_value = city.city_value;
            let html = `<button type="button" class="btn shop_options_location_option shop_options_location_option_btn global_font_3 global_remove_shadow" value="${city_id}">${city_value}</button>`;
            $('.shop_options_location_select').empty().append(html);
            let html_mobi = `<button type="button" class="btn shop_options_location_option_mobi shop_options_location_option_btn global_font_3 global_remove_shadow" value="${city_id}">${city_value}</button>`;
            $('.shop_options_location_select_mobi').empty().append(html_mobi);
        }
    })
    .catch((err) => {
        console.log(err);
    })
});

// $('.shop_options_location_option_btn').on('click', function() {
//     $('.shop_options_location_option_btn').removeClass('active');
//     $(this).addClass('active');
//     let city_id = $(this).attr('data-city-id');
//     const url = window.location.pathname;
//     const id = url.substring(url.lastIndexOf('/') + 1);
//     let axios_url;
//     if (url.includes(id)) {
//         axios_url = `http://host.docker.internal:3000/products/${id}/get_shipping_rate_on_change?city_id=${city_id}`
//         axios.get(axios_url)
//         .then((response) => {
//             console.log(response);
//             // todo: make change method
//         })
//         .catch((error) => {
//             console.log(error);
//         })
//     }
//     else {
//         axios_url = `http://host.docker.internal:3000/products/get_shipping_rates?city_id=${city_id}`
//         axios.get(axios_url)
//         .then((response) => {
//             console.log(response);
//             const products_w_shipping_list = response.data;
//             for (let item of products_w_shipping_list) {
//                 let product_details = item.product;
//                 let shipping_details = item.shipping_rate;
//                 $('.product_item').each(function() {
//                     if ($('input[name=sort_option]') || $('input[name=filter_option]').is(':checked')) {
//                         // todo: make filter method
//                     }
//                 })
//             }
//         })
//     }
// });

$('.shop_options_location_option_btn').on('click', () => {
    $('.shop_options_location_option_btn').removeClass('active');
    $(this).addClass('active');
    let city_id = $(this).val();
    const url = window.location.pathname;
    const id = url.substring(url.lastIndexOf('/') + 1);
    if (url.includes(id)) {
        let axios_url = `http://host.docker.internal:3000/products/${id}/get_shipping_rate_on_change?city_id=${city_id}`;
        axios.get(axios_url)
        .then((res) => {
            //something
        })
        .catch((err) => {
            console.log(err);
        })
    }
    else {
        filter_on_change();
    }
})

function get_city_id() {
    if ($('.shop_options_location_option_btn').hasClass('active')) {
        let city_id = $(this).val();
    }
    else {
        city_id = null;
    }
    return city_id;
}

exports.get_city_id = get_city_id;
const axios = require('axios');
const $ = require('jquery');
const {product_func} = require('./products.js');
const {global} = require('../../config.js');

function place_filter_options(type, type_id, type_value) {
    let ul_cont = `.shop_options_filter_submenu_${type}`;
    let nav_line_class = `shop_options_filter_submenu_${type}_line`;
    let input_id = `shop_options_filter_${type}_${type_value}`
    let universal_class = `shop_options_filter_${type}`;
    let html = `<div class="row shop_options_filter_sub">\n
                    <div class="col">\n
                        ${type_value}\n
                    </div>\n
                    <div class="col-2 shop_options_checkbox_col custom-control custom-checkbox">\n
                        <input id="${input_id}" type="checkbox" name="filter_option" data-filter-type-id="${type_id}" data-filter-option-type="${type}" class="custom-control-input" />\n
                        <label for="${input_id}" class="custom-control-label ${universal_class}">\n
                            <span class="sr-only"></span>\n
                        </label>\n
                    </div>\n
                </div>\n
                <li class="nav_dropdown_line ${nav_line_class}"><img src="/public/global_assets/nav_assets/nav_line_dropdown.png" alt=""></li>`;
    $(ul_cont).empty();
    $(html).appendTo(ul_cont);
    $(`.${nav_line_class}`).last().remove();
    let ul_cont_mobi = `.shop_options_filter_submenu_mobi_${type}`;
    let nav_line_class_mobi = `shop_options_filter_sub_${type}_line_2`;
    let input_id_mobi = `${input_id}_mobi`
    let html_mobi = `<div class="row shop_options_filter_sub_mobi">\n
                        <div class="col shop_options_text_col_mobi my-auto">\n
                            ${type_value}\n
                        </div>\n
                        <div class="col shop_options_checkbox_col_2_mobi custom-control custom-checkbox ml-auto my-auto">\n
                            <input id="${input_id_mobi}" type="checkbox" name="filter_option" data-filter-type-id="${type_id}" data-filter-option-type="${type}" class="custom-control-input ${universal_class}" />\n
                            <label for="${input_id_mobi}" class="custom-control-label">\n
                                <span class="sr-only"></span>\n
                            </label>\n
                        </div>\n
                    </div>\n
                    <li class="shop_options_filter_sub_line_2 ${nav_line_class_mobi}"><img src="/public/global_assets/nav_assets/nav_line_dropdown.png" alt=""></li>`;
    $(ul_cont_mobi).empty();
    $(html_mobi).appendTo(ul_cont_mobi);
    $(`.${nav_line_class_mobi}`).last().remove();
};

$(() => {
    axios.get(`${global.ngrok_api_url}/brands/`, {
        headers: global.headers
    })
    .then((response) => {
        console.log(response);
        const brands = response.data;
        for (let item of brands) {
            let brand = 'brand';
            let brand_id = item.brand_id;
            let brand_value = item.brand_value;
            place_filter_options(brand, brand_id, brand_value);
        }
    }).catch((error) => {
        console.log(error);
    });
    axios.get(`${global.ngrok_api_url}/categories/`, {
        headers: global.headers
    })
    .then((response) => {
        console.log(response);
        const categories = response.data;
        for (let item of categories) {
            let category = 'category';
            let category_id = item.category_id;
            let category_value = item.category_value;
            place_filter_options(category, category_id, category_value);
        }
    })
    .catch((error) => {
        console.log(error);
    });
});

function get_city_id() {
    let city_id = $('.shop_options_location_option_btn.active').val();
    if (city_id === undefined) {
        city_id = null;
    }
    return city_id;
}

function filter_on_change(e) {
    let sort_value;
    console.log($(this));
    if ($(this).prop('name') === 'sort_option') {
        if ($(this).is(':checked')) {
            $(`input:checkbox[name='sort_option']`).not(this).prop('checked', false);
        }
    }
    kwargs = {};
    sort_value = $(`input:checkbox[name='sort_option']:checked`).data('sort-value');
    if (sort_value !== null || undefined) {
        kwargs['sort'] = sort_value;
    }
    let brand_values = [];
    let category_values = [];
    $(`input:checkbox[name='filter_option']:checked`).each(() => {
        let array;
        let filter_type = $(this).data('filter-option-type');
        if (typeof filter_type !== 'undefined') {
            if (filter_type === 'category') {
                array = category_values;
            }
            if (filter_type === 'brand') {
                array = brand_values;
            }
            array.push($(this).data('filter-type-id'));
        }
    });
    if (category_values.length !== 0) {
        kwargs['filter_category'] = category_values;
    }
    console.log(category_values);
    if (brand_values !== 0) {
        kwargs['filter_brand'] = brand_values;
    }
    console.log(brand_values);
    let city_id = get_city_id();
    if (city_id !== null) {
        kwargs['city_id'] = city_id;
    }
    product_func.get_products(kwargs);
}

// function filter_on_change(e) {
//     let sort_value;
//     console.log($(this));
//     if ($(this).is(':checked')) {
//         if ($(this).prop('name') === 'sort_option') {
//             $(`input:checkbox[name='sort_option']`).not(this).prop('checked', false);
//         }
//     }
//     sort_value = $(`input:checkbox[name='sort_option']`).val();
//     if (sort_value === undefined || null) {
//         sort_value = null;
//     }
//     let brand_values = [];
//     let category_values = [];
//     $(`input:checkbox[name='filter_option']:checked`).each(() => {
//         let array;
//         let filter_type = $(this).data('filter-option-type');
//         if (filter_type === 'category') {
//             array = category_values;
//         }
//         if (filter_type === 'brand') {
//             array = brand_values;
//         }
//         array.push($(this).val());
//     });
//     if (category_values.length === 0) {
//         category_values = null;
//         console.log(category_values);
//     }
//     if (brand_values === 0) {
//         brand_values = null;
//         console.log(brand_values);
//     }
//     let city_id = get_city_id();
//     product_func.get_products(sort_value, brand_values, category_values, city_id);
// }

$(document).on('change', 'input:checkbox', filter_on_change)

export {filter_on_change}
    // let sort_value;
    // if ($('input:checkbox[name=sort_option]').is(':checked')) {
    //     sort_value = $(this).val();
    // }
    // else {
    //     sort_value = null;
    // }
    // let brand_values;
    // let category_values;
    // $('input[name=filter_option]').on('click', function() {
    //     let array;
    //     let filter_type = $(this).attr('data-filter-option-type');
    //     if (filter_type === 'brand') {
    //         array = brand_values;
    //     }
    //     if (filter_type === 'category') {
    //         array = category_values;
    //     }
    //     if ($(this).is(':checked')) {
    //         array.push($(this).val());
    //     }
    //     else {
    //         if ((index = array.indexOf($(this).val())) !== -1) {
    //             array.splice(index, 1);
    //         }
    //     }
    // })
    // if (brand_values.length === 0) {
    //     brand_values = null;
    // }
    // if (category_values.length === 0) {
    //     category_values = null;
    // }
    // let city_id = get_city_id();
    // get_products(sort_value, brand_values, category_values, city_id);

// $('input:checkbox').on('change', () => {
//     filter_on_change();
//     console.log('checkbox clicked');
// });

// function filter_or_sort() {
//     if ($(this).is(':checked')) {
//         let name_attr = $(this).attr('name');
//         const product_divs = $('.product_item_row > .p-2');
//         let product_name_attr = '[data-product-name]'
//         if (name_attr === 'sort_option') {
//             let sort_option_value = $(this).attr('value');
//             let ordered;
//             if (sort_option_value === 'asc_sort') {
//                 ordered = product_divs.sort(function(a, b) {
//                     return $(a).attr(product_name_attr) - $(b).attr(product_name_attr);
//                 });
//             }
//             if (sort_option_value === 'desc_sort') {
//                 ordered = product_divs.sort(function(a, b) {
//                     return $(b).attr(product_name_attr) - $(a).attr(product_name_attr);
//                 });
//             }
//             $('.product_item_row').empty().append(ordered);
//         }
//         if (name_attr === 'filter_option') {
//             let filter_option_value = $(this).attr('value');
//             let filter_option_data_value;
//             if ($(this).hasClass('shop_options_filter_brand')) {
//                 filter_option_data_value = `[data-brand-id=${filter_option_value}]`;
//             }
//             if ($(this).hasClass('shop_options_filter_category')) {
//                 filter_option_data_value = `[data-category-id=${filter_option_value}]`;
//             }
//             product_divs.filter($(filter_option_data_value));
//         }
//     }
// }

// $('input:checkbox').on('change', function() {
//     console.log('selected');
//     if ($(this).is(':checked')) {
//         let name_attr = $(this).attr('name');
//         console.log(name_attr);
//         const product_div = $('.product_item_row > .p-2');
//         const product_div_array = product_div.toArray();
//         const parent_product_div = $('.product_item_row');
//         if (name_attr === 'sort_option') {
//             let sort_option_value = $(this).attr('value');
//             if (sort_option_value === 'asc_sort') {
//                 if (parent_product_div.hasClass('asc_sorted')) {
//                     // do nothing
//                 }
//                 if (parent_product_div.hasClass('desc_sorted')) {
//                     parent_product_div.removeClass('desc_sorted');
//                     parent_product_div.addClass('asc_sort');
//                     product_div_array.reverse();
//                 }

//             }
//             if (sort_option_value === 'desc_sort') {
//                 if (parent_product_div.hasClass('desc_sorted')) {
//                     // do nothing
//                 }
//                 if (parent_product_div.hasClass('asc_sorted')) {
//                     parent_product_div.removeClass('asc_sorted');
//                     parent_product_div.addClass('desc_sorted');
//                     product_div_array.reverse();
//                 }

//             }
//             console.log(product_div_array);
//             $('.product_item_row').empty().append(product_div_array);
//         }
//         if (name_attr === 'filter_option') {
//             let filter_option_value = $(this).attr('value');
//             let filter_option_data_value;
//             if ($(this).hasClass('shop_options_filter_brand')) {
//                 filter_option_data_value = `[data-brand-id=${filter_option_value}]`;
//             }
//             if ($(this).hasClass('shop_options_filter_category')) {
//                 filter_option_data_value = `[data-category-id=${filter_option_value}]`;
//             }
//             product_divs.filter($(filter_option_data_value));
//         }
//     }
// })
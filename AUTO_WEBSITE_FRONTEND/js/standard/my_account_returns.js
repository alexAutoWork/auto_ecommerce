const $ = require('jquery');
const axios = require('axios');
const {check_user} = require('./sens');
const {global} = require('../../config');
const {load_bulk, page_main_load} = require('./my_account_global_items');
import {gen_func} from '../shared/shared_gen_func';
import {event_func} from '../shared/shared_event_func';

let user_state = [false, false]

$(() => {
    user_state = check_user();
    gen_func.return_auth_page(user_state, {render_1: get_returns, render_2: get_returns_page});
})

function get_returns() {
    load_bulk('return');
}

function get_returns_page(return_id) {
    const axios_url = `${global.ngrok_api_url}/auth/returns/${return_id}/`
    axios.get(axios_url, global.options)
    .then((res) => {
        data = res.data;
        page_main_load(data, 'return');
        $('.my_account_main_indi_item_reason_return').text(data.reason_return);
        $('.my_account_main_indi_item_product_problem').text(data.product_problem);
        $('.my_account_main_indi_item_preferred_outcome').text(data.preferred_outcome);
    })
    .catch((err) => {
        console.log(err);
    })
}

$('.my_account_return_btn').on('click', () => {
    $('#my_account_apply_for_return_popup1').modal('show');
    $('.my_account_apply_for_return_back').on('click', () => {
        event_func.toggle_slide('back');
    })
    const axios_url = `${global.ngrok_api_url}/auth/orders/`;
    axios.get(`${axios_url}?is_completed=True`, global.options)
    .then((res) => {
        const data = res.data;
        for (let item of data) {
            let template = $('.my_account_apply_for_return_indi_order_cont').clone();
            template.find('.my_account_apply_for_return_order_number').text(`order #${item.order_id}`);
            template.find('my_account_apply_for_return_order_date').text(`order date ${item.order_date}`);
            template.data('order-id', item.order_id);
            template.data('order-date', item.order_date)
            template.appendto('#my_account_apply_for_return_orders_cont').show();
        }
        let order_id = null;
        let order_date = null;
        $('.my_account_apply_for_return_indi_item_cont').on('click', () => {
            $('.my_account_apply_for_return_indi_item_cont').removeClass('active');
            $(this).addClass('active');
            order_id = $(this).data('order-id');
            order_date = $(this).data('order-date');
        })
        $('#my_account_apply_for_return_select_order_next').on('click', () => {
            if (order_id !== null && order_date !== null) {
                event_func.toggle_slide('next');
                axios.get(`${axios_url}${order_id}/retrieve_items/`, global.options)
                .then((res) => {
                    const item_data = res.data;
                    for (let item of item_data) {
                        let item_template = $('.my_account_apply_for_return_indi_order_item_cont').clone();
                        let sku_no = item.sku_no;
                        let product_config_id = sku_no.product_config_id;
                        let product_id = product_config_id.product_id;
                        let img_location = `/public/${product_id.product_img_thumb}`;
                        item_template.find('.my_account_apply_for_return_item_img_cont').append(
                            `<img src="${img_location}" class="my_account_apply_for_return_item_img">`
                        )
                        item_template.find('my_account_apply_for_return_item_name').text(product_id.name);
                        item_template.find('my_account_apply_for_return_item_type').text(`type: ${product_config_id.variation_value}`);
                        item_template.find('my_account_apply_for_return_item_price').text(`R${item.order_item_excl}`);
                        item_template.find('my_account_apply_for_return_item_number').text(`ITEM NO: #${sku_no}`);
                        item_template.data('order-item-id', item.order_item_id).appendto('#my_account_apply_for_return_order_items_cont').show();
                    }
                    let order_item_id = null;
                    let order_item_preview = null;
                    $('.my_account_apply_for_return_indi_order_item_cont').on('click', () => {
                        $('.my_account_apply_for_return_indi_item_cont').removeClass('active');
                        $(this).addClass('active');
                        order_item_id = $(this).data('order-item-id');
                        order_item_preview = $(this).clone();
                    })
                    $('#my_account_apply_for_return_select_item_next').on('click', () => {
                        if (order_item_id !== null && order_item_preview !== null) {
                            event_func.toggle_slide('next');
                            order_item_preview.appendto('.my_account_apply_for_return_item_prev_cont');
                            let reason_return = $('#my_account_apply_for_return_reason_input').val();
                            let problem_product = $('#my_account_apply_for_return_problem_input').val();
                            let preferred_outcome = $('#my_account_apply_for_return_preferred_outcome_input').val();
                            $('#my_account_apply_for_return_reason_next').on('click', () => {
                                $('.my_account_apply_for_return_review_return_input_cont').append(
                                    `<p>reason for return:</p>\n
                                    <p>${reason_return}</p>\n
                                    <p>problem with product:</p>\n
                                    <p>${problem_product}</p>\n
                                    <p>preferred outcome:</p>\n
                                    <p>${preferred_outcome}</p>\n`
                                )
                                $('#my_account_apply_for_return_review_return_next').on('click', () => {
                                    event_func.toggle_slide('next');
                                    const data = {
                                        order_id: order_id,
                                        order_item_id: order_item_id,
                                        reason_return: reason_return,
                                        problem_product: problem_product,
                                        preferred_outcome: preferred_outcome
                                    }
                                    axios.post(`${global.ngrok_api_url}/auth/returns/`, data, global.options)
                                    .then((res) => {
                                        $('.my_account_apply_for_return_res_message').text(res.data.message);
                                    })
                                    .catch((err) => {
                                        console.log(err);
                                    })
                                })
                            })
                        }
                    })
                })
                .catch((err) => {
                    console.log(err);
                })
            }
        })
    })
    .catch((err) => {
        console.log(err);
    })
})

// $(function() {
//     $('.my_account_main_item_cont').remove();
//     const url = `http://host.docker.internal:3000/auth/returns`;
//     axios.get(url, {
//         headers: token
//     })
//     .then((response) => {
//         const user_returns = response.data;
//         let user_past_returns_html_array = [];
//         let user_current_returns_html_array = [];
//         for (let user_return of user_returns) {
//             let return_id = user_return.return_id;
//             let img_location = `/public/${user_return.product_img_thumb}`;
//             let status_value = user_return.current_status_value;
//             let status_date = user_return.current_status_date
//             let html = 
//             `<div class="container my_account_main_item_cont">\n
//                 <div class="row">\n
//                     <div class="col">\n
//                         <div class="d-flex flex-column my_account_main_item_number_and_img_cont">\n
//                             <div class="p-2 my_account_main_item_number_cont">\n
//                                 <div class="row">\n
//                                     <div class="col-10 my_account_main_item_number_col">\n
//                                         <p class="my_account_main_item_number">RETURN #${return_id} / ITEM #${user_return.sku_no}</p>\n
//                                     </div>\n
//                                     <div class="col my_account_main_item_view_mobi_cont text-right">\n
//                                         <button type="button" class="btn global_font_3 global_remove_shadow global_white_select_btn d-sm-block d-md-none my_account_main_item_view_mobi"><i class="fa-solid fa-chevron-right"></i>\n
//                                     </div>\n
//                                 </div>\n
//                             </div>\n
//                             <div class="p-2 my_account_main_item_status_cont d-block d-md-none">\n
//                                 <p class="my_account_main_item_status">STATUS: ${status_value}</p>\n
//                                 <p>STATUS DATE: ${status_date}</p>\n
//                             </div>\n
//                             <div class="d-flex flex-row p-2 my_account_main_indi_item_img_cont">\n
//                                 <div class="p-2 my_account_main_indi_item_img_cont_inner">\n
//                                     <img src="${img_location}" class="my_account_main_indi_item_img">\n
//                                 </div>\n
//                             </div>\n
//                         </div>\n
//                     </div>\n
//                     <div class="col d-none d-md-block">\n
//                         <div class="d-flex flex-column my_account_main_item_btn_col">
//                             <div class="p-2 ml-md-auto ml-lg-auto ml-xl-auto text-right">\n
//                                 <p class="my_account_main_item_status">STATUS: ${status_value}</p>\n
//                                 <p>STATUS DATE: ${status_date}</p>\n
//                             </div>\n
//                             <div class="p-2 mt-md-auto ml-md-auto mt-lg-auto ml-lg-auto mt-xl-auto ml-xl-auto">\n
//                                 <button type="button" class="btn global_red_select_btn_2 global_remove_shadow">RETURN DETAILS</button>\n
//                             </div>\n
//                         </div>\n
//                     </div>\n
//                 </div>\n
//             </div>`
//             let is_completed = user_return.is_completed;
//             if (is_completed === true) {
//                 user_past_returns_html_array.push(html);
//             }
//             else {
//                 user_current_returns_html_array.push(html);
//             }
//         }
//         if (user_past_returns_html_array.length !== 0) {
//             $(user_past_returns_html_array).insertAfter('.my_account_past_returns_header');
//         }
//         if (user_current_returns_html_array.length !== 0) {
//             $(user_current_returns_html_array).insertAfter('#my_account_apply_for_return_popup1');
//         }
//     })
//     .catch((error) => {
//         console.log(error);
//     })
// });

// $('.my_account_return_btn').on('click', function() {
//     $('#my_account_apply_for_return_popup1').modal('show');
      
// })

// $(document).ready(function () {
// 	$('#my_account_apply_for_return_select_item_cont').hide();
// 	$('#my_account_apply_for_return_reason_cont').hide();
// 	$('#my_account_apply_for_return_review_return_cont').hide();
// 	$('#my_account_apply_for_return_success_cont').hide();
// });

// $('#my_account_apply_for_return_select_order_next').on('click', function() {
// 	$('#my_account_apply_for_return_select_order_cont').slideUp();
// 	$('#my_account_apply_for_return_select_item_cont').slideDown();
// });

// $('#my_account_apply_for_return_select_item_next').on('click', function() {
// 	$('#my_account_apply_for_return_select_item_cont').slideUp();
// 	$('#my_account_apply_for_return_reason_cont').slideDown();
// });

// $('#my_account_apply_for_return_reason_next').on('click', function() {
// 	$('#my_account_apply_for_return_reason_cont').slideUp();
// 	$('#my_account_apply_for_return_review_return_cont').slideDown();
// })

// $('#my_account_apply_for_return_review_return_next').on('click', function() {
// 	$('#my_account_apply_for_return_review_return_cont').slideUp();
// 	$('#my_account_apply_for_return_success_cont').slideDown();
// });

// $('.my_account_apply_for_return_indi_item_cont').on('click', function() {
	
// 	if ($(this).hasClass('item_selected')) {
// 		$(this).removeClass('item_selected');
// 	}
// 	else {
// 		$('.my_account_apply_for_return_indi_item_cont').removeClass('item_selected');
// 		$(this).addClass('item_selected');
// 	}
// });

// $('#my_account_apply_for_return_reason_cont .my_account_apply_for_return_indi_item_cont').removeAttr('onclick').off('click');
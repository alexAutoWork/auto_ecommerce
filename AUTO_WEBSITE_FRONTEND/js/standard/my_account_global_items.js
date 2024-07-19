const axios = require('axios');
const $ = require('jquery');
import {gen_func} from '../shared/shared_gen_func';
import {render_func} from '../shared/shared_render_func';
const {global} = require('../../config');

function load_bulk(type) {
    const axios_url = `${global.ngrok_api_url}/auth/${type}s`;
    axios.get(axios_url, global.options)
    .then((res) => {
        data = res.data;
        for (let item of data) {
            let template = $('.my_account_main_item_cont').clone();
            let type_id = gen_func.get_prop(item, `${type}_id`);
            let status_value = item.status_value;
            let status_date = item.current_status_date;
            let detail_url = `/${type}/${type_id}`;
            let is_completed = item.is_completed;
            let item_number = `${type} #${type_id}`
            let product_id;
            if (type === 'return') {
                let sku_no = item.order_item_id.sku_no;
                product_id = sku_no.product_config_id.product_id;
                item_number = item_number + ` / ITEM #${sku_no}`;
            }
            if (type === 'invoice') {
                let order_id = item.order_id;
                item_number = item_number + ` / ORDER #${order_id}`;
            }
            if (type === 'repair') {
                product_id = item.product_id;
            }
            if (product_id !== null || undefined) {
                let item_img_cont = 'my_account_main_indi_item_img_cont'
                let product_img_url = product_id.product_img_thumb;
                let product_img_html =
                `<div class="p-2 my_account_main_indi_item_img_cont_inner">\n
                    <img src="/public/${product_img_url}" class="my_account_main_indi_item_img">\n
                </div>\n`
                template.find(item_img_cont).show().append(product_img_html);
            }
            template.find('.my_account_main_item_status').text(`STATUS: ${status_value}`);
            template.find('.my_account_main_item_status_date').text(`STATUS DATE: ${status_date}`);
            let cont;
            let details_btn;
            if (status_value !== 'saved') {
                details_btn = 
                `<button type="button" class="btn global_red_select_btn_2 global_remove_shadow" onclick="window.location.href='${detail_url}';">${type} DETAILS</button>`;
                if (is_completed) {
                    cont = 'completed';
                }
                else {
                    cont = 'pending';
                }
            }
            else {
                detail_url = `/checkout/${detail_url}`;
                details_btn = 
                `<button type="button" class="btn global_red_select_btn_2 global_remove_shadow" onclick="window.location.href='${detail_url}';">CONTINUE PURCHASE</button>`;
                cont = status_value;
            }
            cont = `my_account_${cont}_cont`;
            template.find('my_account_main_item_btn_cont').text(details_btn);
            template.show();
            template.appendTo(`my_account_${cont}_cont`);
        }
    })
    .catch((err) => {
        console.log(err);
    })
}

function page_main_load(data, type) {
    let template = $('my_account_main_indi_item_cont').clone();
    let type_id = gen_func.get_prop(data, `${type}_id`);
    let id_header = `${type} #${type_id}`
    let date = gen_func.get_prop(data, `${type}_date`);
    if (type === 'return') {
        let order_id = data.order_id;
        let sku_no = data.order_item_id.sku_no;
        id_header = `${id_header} / ITEM #${sku_no}`
    }
    template.find('.my_account_main_indi_item_number_header').text(id_header);
    template.find('.my_account_main_indi_item_date').text(`${type} date: ${date}`);
    template.find('.my_account_main_indi_item_status').text(`status: ${data.current_status_value} / status date: ${data.current_status_date}`);
    let shipping_tracking_id = gen_func.get_prop(data, 'shipping_tracking_id', return_null=true);
    if (shipping_tracking_id !== null) {
        template.find('my_account_main_indi_item_tracking_number').show().text(`TRACKING NO #${shipping_tracking_id}`);
        template.find('my_account_main_indi_item_courier').show();
    }
    let shipping_method_value = gen_func.get_prop(data, 'shipping_method_value');
    if (shipping_method_value !== null) {
        template.find('my_account_main_indi_item_delivery').text(shipping_method_value);
        if (shipping_method_value === 'deliver with our courier') {
            let shipping_address_id = gen_func.get_prop(data, 'shipping_address_id');
            let address_html = render_func.render_shipping(shipping_address_id);
            template.find('my_account_main_indi_item_shipping_cont').append(address_html).show();
        }
    }
    page_extra_load(data, type);
}

function page_extra_load(data, type) {
    load_summary(data, type);
    let is_repair = false;
    let item_data;
    switch (type) {
        case 'repair':
            is_repair = true;
            item_data = [data.product_id];
            break;
        case 'order':
            item_data = data;
            break;
        case 'return':
            item_data = [data.order_item_id];
            break;
        default:
            throw new Error('type is invalid!');
    }
    render_func.render_items(item_data, is_repair);
    history_data = gen_func.get_prop(data, `${type}_history`, return_null=true);
    if (history_data !== null) {
        render_func.render_history(data)
    }
}

export {load_bulk, page_extra_load}
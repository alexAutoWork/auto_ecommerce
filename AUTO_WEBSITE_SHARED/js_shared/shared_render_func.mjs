const {get_prop_by_string} = import('./shared_gen_func.mjs');

function initialize_address(shipping_address_id) {
    const excluded = ['address_id', 'user_id', 'name', 'is_active', 'is_default'];
    let address = [];
    let excluded_values = [];
    for (let [key, value] of Object.entries(shipping_address_id)) {
        if (value !== null) {
            if (excluded.some(i => key.includes(i))) {
                excluded_values.push(value);
            }
            else {
                address.push(`${value}<br>\n`);
            }
        }
    }
    let name = excluded_values[2];
    address = address.toString();
    return [address, excluded_values]
}

function load_shipping_details(shipping_address_id, return_excluded=false) {
    [address, excluded_values] = initialize_address(shipping_address_id);
    let name = excluded_values[2]
    let address_html =
    `<p class="global_font_4 global_font_italic">${name}</p>\n
    <p class="global_font_4 global_font_italic">${address}</p>\n`;
    let return_value;
    if (return_excluded) {
        return_value = [address_html, excluded_values]
    }
    else {
        return_value = address_html
    }
    return return_value
}

function initialize_summary(data, type) {
    let extra = null
    let shipping;
    let subtotal;
    let tax;
    let total;
    if (type === 'order') {
        extra = {
            quantity: `${data.order_quantity} items`,
            excl: `R${data.subtotal_excl}`,
        };
        shipping = data.shipping_price;
        subtotal = data.order_subtotal_incl;
        tax = data.order_tax;
        total = data.order_total;
    }
    if (type === 'repair') {
        shipping = data.shipping_price_excl;
        subtotal = null;
        tax = data.shipping_price_tax;
        total = data.shipping_price_incl;
    }
    const fields = {
        shipping: shipping,
        subtotal: subtotal,
        tax: tax
    }
    return [fields, extra, total]
}

function load_summary(data, type) {
    let template = '<tbody class="item_summary_body"></tbody>'
    [fields, extra, total] = initialize_summary(data, type)
    let rows = [];
    if (extra !== null) {
        rows.push(
        `<td class="my_account_main_indi_item_price_summary_head">${extra.quantity} ITEMS</td>\n
        <td class="my_account_main_indi_item_price_summary_table_data global_font_italic_bold">R${extra.excl}</td>`
        );
    }
    for (let [key, value] of fields) {
        rows.push(
        `<td class="my_account_main_indi_item_price_summary_head">${key}</td>\n
        <td class="my_account_main_indi_item_price_summary_table_data global_font_italic_bold">R${value}</td>`
        );
    } 
    rows.push(
    `<td class="my_account_main_indi_item_price_summary_head">TOTAL</td>
    <td class="my_account_main_indi_item_price_summary_table_data global_font_italic_bold my_account_main_indi_item_price_summary_table_total">R${total}</td>`
    );
    let tbody = $(template).find('tbody');
    for (let row of rows) {
        $(
            `<tr class="my_account_main_indi_item_price_summary_table_row">${row}</tr>`
        ).appendTo(tbody);
    }
    return tbody
}

function initalize_items(data, repair=false) {
    let items = [];
    let product_id;
    let vals = [
        {order_item_excl: 'item.order_item_excl'}, 
        {sku_no: 'item.sku_no'}, 
        {variation_value: 'item.sku_no.product_config_id.variation_value'}
    ]
    for (let item of data) {
        if (repair) {
            product_id = item;
        } else {
            product_id = item.sku_no.product_config_id.product_id;
        }
        let img_location = `/public/${product_id.product_img_thumb}`;
        let base = {img_location: img_location, name: product_id.name}
        for (const val of vals) {
            for (let [key, value] of Object.entries(val)) {
                let attr = get_prop_by_string(item, value, true);
                base.append(key, attr);
            }
        }
        items.push(base);
    }
    return items;
}

function load_items(data, repair=false) {
    const items = initalize_items(data, repair);
    let item_html = [];
    for (let item of items) {
        let template =
        `<div class="container items_product_cont">\n
            <div class="d-flex flex-row items_product_cont_flex">\n
                <div class="p-2 order_conf_order_items_product_img">\n
                    ${item.img_location}\n
                </div>\n
                <div class="p-2 product_details_cont">\n
                    <p class="global_font_3 product_details_name">${item.name}</p>\n
                </div>
            </div>\n
        </div>\n
        <hr>\n`
        $('.product_details_name').text(product_id.name);
        let order_item_excl = item.order_item_excl;
        if (order_item_excl !== null) {
            let item_html = 
            `<p class="global_font_4 global_font_italic product_details_type">TYPE: ${item.variation_value}</p>\n
            <p class="global_font_4 global_font_italic product_details_sku">SKU NO: ${item.sku_no}</p>\n
            <p class="global_font_3 d-block d-sm-block d-md-none">R${order_item_excl}</p>\n`
            let item_html_mobi = 
            `<div class="p-2 product_details_price d-none d-sm-none d-md-block d-lg-block d-xl-block">\n
                <p class="global_font_3">R${order_item_excl}</p>\n
            </div>\n`
            template.find('.product_details_cont').append(item_html);
            template.find('.items_product_cont_flex').append(item_html_mobi);
        }
        item_html.push(template);
    }
    return item_html
}

function load_history(data) {
    let table = $('table.my_account_main_indi_item_status_history > tbody');
    let table_mobi = $('table.my_account_status_history_table_mobi > tbody');
    for (let item of data) {
        let history = 
        `<tr>\n
            <td>${item.status_date}</td>\n
            <td>${item.status_value}</td>\n
            <td>${item.status_comment}</td>\n
        </tr>\n`
        history.appendto(table);

        let history_mobi =
        `<tr>\n
            <td class="global_font_3 global_font_no_italic">DATE</td>\n
            <td>${item.status_date}</td>\n
        <tr>\n
        <tr>\n
            <td class="global_font_3 global_font_no_italic">STATUS</td>\n
            <td>${item.status_value}</td>\n
        <tr>\n
        <tr>\n
            <td class="global_font_3 global_font_no_italic">COMMENT</td>\n
            <td>${item.status_comment}</td>\n
        <tr>\n`

        history_mobi.appendto(table_mobi);
    }
}

export {load_shipping_details, load_summary, load_items, load_history, initialize_address, initialize_summary, initalize_items}
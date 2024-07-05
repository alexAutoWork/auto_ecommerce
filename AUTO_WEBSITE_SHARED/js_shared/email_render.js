const jsdom = require('jsdom');
const fs = require('fs');
const path = require('path');
const {initialize_address, initialize_summary, initalize_items} = require('./shared_render_func');
const { get_prop_by_string } = require('./shared_gen_func');
const { get } = require('jquery');

function new_otp_email(data) {
    const main_html = fs.readFile(path.join(__dirname, `../../html/shared/otp_email.html`));
    const dom = new jsdom.JSDOM(main_html);

    const $ = require('jquery')(dom.window);

    for (let [key, value] of Object.entries(data)) {
        let element = main_html.find(`[data-insert-value='${key}']`)
        if (element !== undefined || null) {
            element.text(value);
        }
    }

    const filename = data.filename

    const main_css = fs.readFile(path.join(__dirname, `../../css/shared/global_email.css`));
    $(`<style>${main_css}</style>`).appendTo('body');

    const content = dom.serialize()

    const path = path.join(__dirname, `../../media/tmp/html/otp/${filename}.html`);

    fs.writeFile(path, content, (err) => {
        if (err) {
            return console.log(err);
        } else {
            return console.log('success!');
        }
    })
    
    return path;
}

function new_status_email(data) {
    const main_html = fs.readFile(path.join(__dirname, `../../html/shared/status.html`));
    const dom = new jsdom.JSDOM(main_html);

    for (let [key, value] of Object.entries(data)) {
        let element = main_html.find(`[data-insert-value='${key}']`)
        if (element !== undefined || null) {
            element.text(value);
        }
    }

    const main_css = fs.readFile(path.join(__dirname, `../../css/shared/global_email.css`));
    $(`<style>${main_css}</style>`).appendTo('body');

    const content = dom.serialize();

    const path = path.join(__dirname, `../../media/${data.obj_type}/${data.type_id}/temp/html/${data.filename}.html`)

    fs.writeFile(path, content, (err) => {
        if (err) {
            return console.log(err);
        } else {
            return console.log('success!');
        }
    })

    return path;
}

function new_conf_email(data) {
    const obj_type = data.obj_type;
    const main_html = fs.readFile(path.join(__dirname, `../../html/shared/${obj_type}_conf_email.html`));
    const dom = new jsdom.JSDOM(main_html);

    main_html.find(`[data-insert-value='type_id']`).text(data.type_id);

    const main_details = get_prop_by_string(data, `${obj_type}_details`, true)
    if (main_details !== null) {
        const shipping_method_value = main_details.shipping_method_value;
        main_html.find(`[data-insert-value='shipping_method_value']`).text(shipping_method_value);
        if (shipping_method_value === 'deliver with our courier') {
            [address, excluded] = initialize_address(main_details.shipping_address_id);
            const name = excluded[2];
            const shipping_address_html = `<p>${name}</p><p>${address}</p>`;
            main_html.$(shipping_address_html).appendTo('#email_conf_shipping_address').show();
        }
        [fields, extra, total] = initialize_summary(main_details, obj_type);
        let rows = [];
        if (extra !== null) {
            rows.push(
                `<td>${extra.quantity}</td>
                <td class="roboto-bold-italic email_conf_table_data">${extra.excl}</td>`
            );
        }
        for (let [key, value] of fields) {
            rows.push(
                `<td>${key}</td>
                <td class="roboto-bold-italic email_conf_table_data">R${value}</td>`
            );
        }
        rows.push(
            `<td class="email_conf_table_blank"></td>
            <td class="email_conf_table_blank"></td>`
        );
        rows.push(
            `<td>total</td>
            <td class="roboto-bold-italic email_conf_table_data">R${total}</td>`
        );
        let summary_cont = main_html.find('table.email_conf_table > tbody');
        for (let row of rows) {
            $(`<tr>${row}</tr>`).appendTo(summary_cont);
        }
        let data_parent = main_details;
        let data_attr;
        let is_repair = false;
        if (obj_type === 'order') {
            data_parent = data
        }
        switch(obj_type) {
            case 'order':
                data_attr = 'order_items';
                break;
            case 'repair':
                data_attr = 'product_id';
                is_repair = true;
                break;
            case 'return':
                data_attr = 'order_item_id';
                break;
        }
        let main_items = get_prop_by_string(data_parent, data_attr)
        if (obj_type !== order) {
            main_items = [main_items];
        }
        main_items = initalize_items(main_items, is_repair);
        for (let item of main_items) {
            let base = main_html.find('.email_conf_item_cont_inner1').clone();
            for (let [key, value] of Object.entries(item)) {
                if (key !== 'img_location') {
                    base.find(`[data-insert-item-value='${key}']`).text(value);
                }
            }
            base.show().appendTo('.email_conf_item_cont');
        }
        if (obj_type === 'repair' || 'return') {
            let summary_cont_2 = main_html.find('.email_conf_summary_cont_2');
            summary_cont_2.find('p').each(() => {
                if (!$(this).hasClass('email_conf_summary_subheader')) {
                    let data_attr = $(this).find(`[data-insert-value]`);
                    let value = get_prop_by_string(main_details, data_attr, true);
                    if (value !== null) {
                        $(this).text(value);
                    }
                }
            })
        }
    }

    const main_css = fs.readFile(path.join(__dirname, `../../css/shared/global_email.css`));
    $(`<style>${main_css}</style>`).appendTo('body');

    const content = dom.serialize();

    const path = path.join(__dirname, `../../media/${data.obj_type}/${data.type_id}/temp/html/${data.filename}.html`);

    fs.writeFile(path, content, (err) => {
        if (err) {
            return console.log(err);
        } else {
            return console.log('success!');
        }
    });

    return path;
}

module.exports = {new_otp_email, new_status_email, new_conf_email};
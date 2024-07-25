const jsdom = require('jsdom');
const fs = require('fs');
const path = require('path');
const jsPDF = require('jspdf');

const invoice_func = {
    invoice_render: function(data) {
        const main_html = fs.readFile(path.join(__dirname, `../../html/my_account_invoices_invoice_page.html`));
        const dom = new jsdom.JSDOM(main_html);
        const $ = require('jquery')(dom.window);
    
        const invoice_items = data.invoice_items;
        delete data.invoice_items;
    
        for (let [key, value] of Object.entries(data)) {
            $(`[data-insert-values='${key}']`).text(value);
        }
    
        const invoice_item_template = $('table.invoice_items_table > tbody > tr').clone();
    
        for (let item of invoice_items) {
            for (let [key, value] of Object.entries(item)) {
                invoice_item_template.find(`[data-insert-item-values='${key}']`).text(value);
            }
            invoice_item_template.appendTo('table.invoice_items_table > tbody');
        }
    
        const main_css = fs.readFile(path.join(__dirname, `../../css/invoice.css`));
        $(`<style>${main_css}</style>`).appendTo('body');
    
        const content = dom.serialize();
    
        const dir = `../media/invoices/${data.invoice_id}`;
        fs.mkdir(dir);
    
        let pdf = new jsPDF();
        pdf.html(content, {
            callback: (pdf) => {
                pdf.save(`${dir}/${data.filename}`);
            }
        })
    }
}

module.exports = {invoice_func};
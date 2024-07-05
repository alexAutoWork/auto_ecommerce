const express = require('express');
const path = require('path');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const bootstrap_email = require('bootstrap-email');
const server_funct = require('./server_functions.js');
const email_render = require('./js/shared/email_render.js');
const invoice_render = require('./js/shared/invoice_render.js')

const whitelist = ['http://localhost:3000', 'http://host.docker.internal:3000'];

const allowed_headers = ['Content-Type', 'Accept', 'Authorization']

const cors_options = {
    origin: whitelist,
    optionsSuccessStatus: 200,
    allowedHeaders: allowed_headers
}

const global_cors = cors(cors_options)

const app = express();

app.use(global_cors);
app.options('*', global_cors);
app.use(express.json());

app.use('/public', express.static('esbuild_js'));
app.use('/public', express.static('assets'));
app.use('/public', express.static('css'));
app.use('/public', express.static('media/product_images'));
app.use('/public', express.static('node_modules/bootstrap/dist/css'));
app.use('/public', express.static('node_modules/bootstrap/dist/js'));
app.use('/public', express.static('node_modules/jquery/dist'));
app.use('/public', express.static('node_modules/@fortawesome/fontawesome-free/css'));
app.use('/public', express.static('node_modules/@fortawesome/fontawesome-free/js'));

app.get('/products', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/standard/products.html');

    res.sendFile(_retfile);
});

app.get('/products/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/standard/products_page.html');

    res.sendFile(_retfile);
})

app.get('/forgot', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/forgot.html');

    res.sendFile(_retfile);
})

app.get('/repair/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/repair_conf.html');

    res.sendFile(_retfile);
})

app.post('render-invoice', async (req, res) => {
    const data = req.body;
    try {
        invoice_render(data);
        res.json({message: 'successful'});
    } catch (err) {
        console.log(err);
    }
})

app.post('/html-email', async (req, res) => {
    const needs_render = req.body.needs_render;
    if (needs_render === true) {
        try {
            const data = req.body;
            const html_type = data.html_template_type;
            let _retfile;
            switch (html_type) {
                case 'OTP':
                    _retfile = await email_render.new_otp_email(data);
                    break;
                case 'conf':
                    _retfile = await email_render.new_status_email(data);
                    break;
                case 'status':
                    _retfile = await email_render.new_conf_email(data);
                default:
                    res.json({message: 'not a valid html type!'});
            }
            const compiled_email = await new bootstrap_email(_retfile);
            compiled_email.compileAndSave(file);
            console.log('compiled');
            res.json({message: 'render successful'});
        } catch (err) {
            console.log(err);
        }
    }
})

app.get('/test', async (req, res) => {
    try {
        const res = await axios.get('http://host.docker.internal:3000/products');
        console.log(res);
    }
    catch (err) {
        console.log(err);
    }
    // res.end();
})

app.get('/checkout/:type/:id', (req, res) => {
    const type = req.params.type;
    let _retfile;
    if (type === 'order') {
        _retfile = path.join(__dirname, './html/standard/auth/checkout.html');
    }
    if (type === 'repair') {
        _retfile = path.join(__dirname, './html/standard/auth/request_repair.html');
    }

    res.sendFile(_retfile);
})

app.get('/:type1/:type2/:id', (req, res) => {
    const type1 = req.params.type1;
    const type2 = req.params.type2;
    let _retfile;
    if (type1 === 'conf') {
        if (type2 === 'order') {
            _retfile = path.join(__dirname, './html/standard/auth/checkout.html');
        }
        if (type2 === 'repair') {
            _retfile = path.join(__dirname, './html/standard/auth/request_repair.html');
        }
    }
    if (type1 === 'cancel') {
        _retfile = path.join(__dirname, './html/standard/auth/checkout_cancel.html');
    }
    res.sendFile(_retfile);
})

app.get('/order-conf/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/other/order_conf.html');

    res.sendFile(_retfile);
})

app.post('/pdf-email', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/other/otp_email.html');

    res.sendFile(_retfile);
})

app.get('/register', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/auth/sign_up.html');

    res.sendFile(_retfile);
})

app.get('/email-html', (req, res) => {
    const _retfile = path.join(__dirname, './html/other/otp_email.html');

    res.sendFile(_retfile);
})

app.get('/email-html-2', (req, res) => {
    const _retfile = path.join(__dirname, './html/other/status_email.html');

    res.sendFile(_retfile);
})

app.get('/order-conf-email', (req, res) => {
    const _retfile = path.join(__dirname, './html/other/order_conf_email.html');

    res.sendFile(_retfile);
})

app.get('/return-conf-email', (req, res) => {
    const _retfile = path.join(__dirname, './html/other/return_conf_email.html');

    res.sendFile(_retfile);
})

app.get('/repair-conf-email', (req, res) => {
    const _retfile = path.join(__dirname, './html/other/repair_conf_email.html');

    res.sendFile(_retfile);
})

app.get('/invoice-email', (req, res) => {
    const _retfile = path.join(__dirname, './html/other/invoice_email.html');

    res.sendFile(_retfile);
})

app.get('/order-conf', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/auth/order_conf.html');

    res.sendFile(_retfile);
})

app.get('/repair-conf', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/repair_conf.html');

    res.sendFile(_retfile);
})

app.get('/return-page', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/auth/my_account_returns_return_page.html');

    res.sendFile(_retfile);
})

app.get('/order-page', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/auth/my_account_orders_order_page.html');

    res.sendFile(_retfile);
})

app.get('/shopping-cart', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/standard/auth/shopping_cart.html');

    res.sendFile(_retfile);
})

app.get('/invoice', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/auth/invoice_download.html');

    res.sendFile(_retfile);
})

app.get('/admin-order-page', (req, res) => {
    const _retfile = path.join(__dirname, './html/admin/admin_orders_order_page.html');

    res.sendFile(_retfile);
})

app.get('/address-book', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/auth/my_account_address_book.html');

    res.sendFile(_retfile);
})

app.listen(8080, () => {
    console.log('Listening on port ' + 8080);
});
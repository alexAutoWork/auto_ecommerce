const express = require('express');
const path = require('path');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const BootstrapEmail = require('bootstrap-email');
const server_funct = require('./server_functions');
// const email_render = require('./js/shared/email_render.mjs');
// import email_render from './js/shared/email_render.mjs';
const email_render = import('./js/shared/email_render.mjs');
const invoice_render = import('./js/shared/invoice_render.mjs');

const whitelist = ['http://localhost:3000', 'http://host.docker.internal:3000', 'https://1f9f-102-68-28-61.ngrok-free.app'];

const allowed_headers = ['Content-Type', 'Accept', 'Authorization', 'ngrok-skip-browser-warning']

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

app.use('/public', express.static('esbuild_js/standard'));
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

app.post('/html-email', (req, res) => {
    const needs_render = req.body.needs_render;
    if (needs_render === true) {
        try {
            const data = req.body;
            const html_type = data.html_template_type;
            let file_attr;
            switch (html_type) {
                case 'OTP':
                    file_attr = email_render.new_otp_email(data);
                    break;
                case 'conf':
                    file_attr = email_render.new_status_email(data);
                    break;
                case 'status':
                    file_attr = email_render.new_conf_email(data);
                default:
                    res.json({message: 'not a valid html type!'});
            }
            const _retfile = file_attr[0];
            const file_path = file_attr[1];
            console.log(_retfile);
            console.log(file_path);
            const start = _retfile.indexOf('/opt/node_app/media');
            const end = start + '/opt/node_app/media'.length;
            const _retfile_sliced = _retfile.slice(0, start) + _retfile.slice(end);
            console.log(_retfile_sliced)
            // const bootstrap_email = new BootstrapEmail(_retfile);
            // const compiled_email = bootstrap_email.compile();
            // fs.writeFileSync(file_path, compiled_email, (err) => {
            //     if (err) {
            //         console.log(err);
            //     } else {
            //         console.log('success!');
            //     }
            // })
            console.log('compiled');
            res.json({message: 'render successful', path: _retfile_sliced});
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
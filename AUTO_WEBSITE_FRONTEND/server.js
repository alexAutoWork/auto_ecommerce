const express = require('express');
const path = require('path');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const BootstrapEmail = require('bootstrap-email');
const server_funct = require('./server_functions');
const {email_render} = require('./js/shared/CJS/email_render');
const {global} = require('./config.js');
const {gen_func} = require('./js/shared/CJS/shared_gen_func');

const whitelist = ['http://localhost:3000', 'http://host.docker.internal:3000', global.ngrok_api_url];

const allowed_headers = ['Content-Type', 'Accept', 'Authorization', 'ngrok-skip-browser-warning', 'Set-Cookie']

const cors_options = {
    origin: whitelist,
    optionsSuccessStatus: 200,
    allowedHeaders: allowed_headers,
    credentials: true
}

const global_cors = cors(cors_options)

const app = express();

app.use(global_cors);
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

const root = '/html/standard'

const urls = {
    products: {
        1: `${root}/standard/products.html`,
        2: `${root}/standard/products_page.html`,
    },
    register: {
        1: `${root}/auth/sign_up.html`
    },
    login: {
        1: `${root}/auth/login.html`
    },
    logout: {
        1: `${root}/auth/logout.html`
    },
    verify: {
        1: `${root}/auth/verify.html`
    },
    forgot: {
        1: `${root}/auth/forgot.html`
    },
    details: {
        1: `${root}/auth/my_account_account_details.html`
    },
    'address-book': {
        1: `${root}/auth/my_account_address_book.html`
    },
    cart: {
        1: `${root}/auth/shopping_cart.html`
    },
    orders: {
        1: `${root}/auth/my_account_orders.html`,
        2: `${root}/auth/my_account_orders_order_page.html`,
    },
    repairs: {
        1: `${root}/auth/my_account_repairs.html`,
        2: `${root}/auth/my_account_repairs_repair_page.html`,
    },
    returns: {
        1: `${root}/auth/my_account_returns.html`,
        2: `${root}/auth/my_account_returns_return_page.html`,
    },
    invoices: {
        1: `${root}/auth/my_account_invoices.html`
    },
    checkout: {
        order: {
            1: `${root}/auth/checkout.html`
        },
        repair: {
            1: `${root}/auth/request_repair.html`
        },
        redirect: {
            1: `${root}/auth/checkout_redirect.html`
        },
        cancel: {
            1: `${root}/auth/checkout_cancel.html`
        }
    },
    conf: {
        order: {
            1: `${root}/auth/order_conf.html`
        },
        repair: {
            1: `${root}/auth/repair_conf.html`
        }
    }
}

app.get('/:base1/:base2?/:base3?', (req, res) => {
    const params = req.params;
    let has_id = false;
    let param_list = [];
    for (let value of Object.values(params)) {
        if (/\d/.test(value)) {
            has_id = true;
        }
        if (typeof value !== 'undefined') {
            param_list.push(value);
        }
    }
    console.log(has_id);
    if (param_list.length === 1) {
        param_list[1] = undefined;
    }
    console.log(param_list);
    let last;
    if (has_id) {
        if (param_list[0] !== 'checkout' || 'conf') {
            last = 2;
        } else {
            last = 1;
        }
    } else {
        last = 1;
    }
    param_list[param_list.length - 1] = last;
    console.log(param_list);
    base_path = param_list.join('.');
    console.log(base_path);
    let _retfile = gen_func.get_prop(urls, base_path);
    if (_retfile === null) {
        _retfile = 1
    }
    console.log(_retfile);
    if (_retfile === 1) {
        res.end();
        return;
    } else {
        res.sendFile(__dirname + _retfile);
        return;
    }
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

app.listen(8080, () => {
    console.log('Listening on port ' + 8080);
});
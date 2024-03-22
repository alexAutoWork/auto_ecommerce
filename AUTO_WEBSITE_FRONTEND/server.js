const express = require('express');
const path = require('path');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const bootstrap_email = require('bootstrap-email');
const server_funct = require('./server_functions.js');
const email_render = require('./js/email_render.js');

const whitelist = ['http://localhost:8000'];

const cors_options = {
    origin: false,
    optionsSuccessStatus: 200
}

// let cors_options_delegate = function(req, callback) {
//     let cors_options;
//     if (whitelist.indexOf(req.header('Origin')) !== -1) {
//         cors_options = {origin: true}
//     } else {
//         cors_options = {origin: false}
//     }
//     callback(null, cors_options)
// }

const app = express();

app.use(cors(cors_options));
app.use(express.json());

app.use('/public', express.static('js'));
app.use('/public', express.static('images'));
app.use('/public', express.static('css'));
app.use('/public', express.static('node_modules/bootstrap/dist/css'));
app.use('/public', express.static('node_modules/bootstrap/dist/js'));
app.use('/public', express.static('node_modules/jquery/dist'));
app.use('/public', express.static('node_modules/popper.js/dist'));
app.use('/public', express.static('node_modules/@fortawesome/fontawesome-free/css'));
app.use('/public', express.static('node_modules/@fortawesome/fontawesome-free/js'));

app.get('/products', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/products.html');

    res.sendFile(_retfile);
});

app.post('/html-email', async (req, res) => {
    const needs_render = req.body.needs_render;
    if (needs_render === true) {
        try {
            const render_data = req.body;
            const html_type = render_data.html_template_type;
            let _retfile;
            switch (html_type) {
                case 'OTP':
                    let _retfile = await email_render.new_otp_email(render_data);
                    break;
                // case 'status':
                //     _retfile = './html/other/otp_email.html';
                //     break;
                // case 'order-conf':
                //     _retfile = './html/other/otp_email.html';
                //     break;
                // case 'repair-conf':
                //     _retfile = './html/other/otp_email.html';
                //     break;
                // case 'return-conf':
                //     _retfile = './html/other/otp_email.html';
                //     break;
                default:
                    res.json({message: 'not a valid html type!'});
            }
            const filename = render_data.filename;
            const file = path.join(__dirname, `../media/html/${filename}.html`)
            const compiled_email = await new bootstrap_email(file);
            compiled_email.compileAndSave(file);
            res.json({message: 'render successful'});
        } catch (err) {
            console.log(err);
        }
        // axios.get('http://172.19.0.3:8000/send-comm/render-email').then((res) => {
        //         render_email_data = res.data;
        //         const html_type = render_email_data.html_template_type;
        //         switch (html_type) {
        //             case 'OTP':
        //                 let _retfile = email_render.new_otp_email(render_email_data);
        //                 break;
        //             // case 'status':
        //             //     _retfile = './html/other/otp_email.html';
        //             //     break;
        //             // case 'order-conf':
        //             //     _retfile = './html/other/otp_email.html';
        //             //     break;
        //             // case 'repair-conf':
        //             //     _retfile = './html/other/otp_email.html';
        //             //     break;
        //             // case 'return-conf':
        //             //     _retfile = './html/other/otp_email.html';
        //             //     break;
        //         }
        //         const filename = render_email_data.filename
        //         const compiled_email = new bootstrap_email(_retfile, './css/global_email.css');
        //         compiled_email.compileAndSave(`./media/html/${filename}.html`);
        //         axios.post('http://172.19.0.3:8000/send-comm/return-email', {'is_rendered': True}).then((res) => {
        //             console.log(res);
        //         }).catch((err) => {
        //             console.log(err);
        //         })
        //     }).catch((err) => {
        //         console.log(err)
        //     })
    }
})

app.post('/test', (req, res) => {
    const message = req.body.message
    if (message === 'sent') {
        res.json({is_send: "sent"}).catch((err) => {
            console.log((err));
        });
    }
    // res.end();
})

app.post('/pdf-email', (req, res) => {
    const _retfile = path.join(__dirname, './html/other/otp_email.html');

    res.sendFile(_retfile);
})

app.get('/register', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/sign_up.html');

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
    const _retfile = path.join(__dirname, './html/auth/order_conf.html');

    res.sendFile(_retfile);
})

app.get('/repair-conf', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/repair_conf.html');

    res.sendFile(_retfile);
})

app.get('/return-page', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/my_account_returns_return_page.html');

    res.sendFile(_retfile);
})

app.get('/order-page', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/my_account_orders_order_page.html');

    res.sendFile(_retfile);
})

app.get('/shopping-cart', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/shopping_cart.html');

    res.sendFile(_retfile);
})

app.get('/invoice', (req, res) => {
    const _retfile = path.join(__dirname, './html/auth/invoice_download.html');

    res.sendFile(_retfile);
})

app.get('/admin-order-page', (req, res) => {
    const _retfile = path.join(__dirname, './html/admin/admin_orders_order_page.html');

    res.sendFile(_retfile);
})

app.listen(3000, () => {
    console.log('Listening on port ' + 3000);
});
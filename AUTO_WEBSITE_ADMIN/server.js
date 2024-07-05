const express = require('express');
const path = require('path');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');

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

app.listen(8060, () => {
    console.log('Listening on port ' + 8060);
});

app.get('/', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_dashboard.html');

    res.sendFile(_retfile);
});

app.get('/products', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_products.html');

    res.sendFile(_retfile);
});

app.get('/products/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_products_product_page.html');

    res.sendFile(_retfile);
});

app.get('/product-stock/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_products_stock_page.html');

    res.sendFile(_retfile);
});

app.get('/product-model/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_products_model_page.html');

    res.sendFile(_retfile);
});

app.get('/orders', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_orders.html');

    res.sendFile(_retfile);
});

app.get('/orders/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_orders_order_page.html');

    res.sendFile(_retfile);
});

app.get('/repairs', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_repairs.html');

    res.sendFile(_retfile);
});

app.get('/repairs/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_repairs_repairs_page.html');

    res.sendFile(_retfile);
});

app.get('/returns', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_returns.html');

    res.sendFile(_retfile);
});

app.get('/returns/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_returns_returns_page.html');

    res.sendFile(_retfile);
});

app.get('/invoices', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_invoices.html');

    res.sendFile(_retfile);
});

app.get('/customers', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_customers.html');

    res.sendFile(_retfile);
});

app.get('/customers/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_customers_customer_page.html');

    res.sendFile(_retfile);
});

app.get('/categories', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_categories.html');

    res.sendFile(_retfile);
});

app.get('/categories/categories/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_categories_category_page.html');

    res.sendFile(_retfile);
});

app.get('/categories/brands/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_categories_brand_page.html');

    res.sendFile(_retfile);
});

app.get('/settings', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_settings.html');

    res.sendFile(_retfile);
});

app.get('/settings/statuses/:id', (req, res) => {
    const _retfile = path.join(__dirname, './html/standard/admin_settings_status_page.html');

    res.sendFile(_retfile);
});
// const $ = require('jquery');
// const pug = require('pug');
// const express = require('express');
// const app = express();

// app.use(express.json());

// app.get('orders/get_queryset', (req, res) => {
// 	req.body;
// 	let json = res.json(req.body);

// })

// const server = await app.listen(3000);

// function return_queryset(json) => {
// 	$()
// }

$('.my_account_address_book_delete_btn').on('click', function() {
	$(this).closest('.my_account_main_item_cont').remove();
});
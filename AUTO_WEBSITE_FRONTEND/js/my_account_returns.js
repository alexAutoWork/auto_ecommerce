$(document).ready(function () {
	$('#my_account_apply_for_return_select_item_cont').hide();
	$('#my_account_apply_for_return_reason_cont').hide();
	$('#my_account_apply_for_return_review_return_cont').hide();
	$('#my_account_apply_for_return_success_cont').hide();
});

$('#my_account_apply_for_return_select_order_next').on('click', function() {
	$('#my_account_apply_for_return_select_order_cont').slideUp();
	$('#my_account_apply_for_return_select_item_cont').slideDown();
});

$('#my_account_apply_for_return_select_item_next').on('click', function() {
	$('#my_account_apply_for_return_select_item_cont').slideUp();
	$('#my_account_apply_for_return_reason_cont').slideDown();
});

$('#my_account_apply_for_return_reason_next').on('click', function() {
	$('#my_account_apply_for_return_reason_cont').slideUp();
	$('#my_account_apply_for_return_review_return_cont').slideDown();
})

$('#my_account_apply_for_return_review_return_next').on('click', function() {
	$('#my_account_apply_for_return_review_return_cont').slideUp();
	$('#my_account_apply_for_return_success_cont').slideDown();
});

$('.my_account_apply_for_return_indi_item_cont').on('click', function() {
	
	if ($(this).hasClass('item_selected')) {
		$(this).removeClass('item_selected');
	}
	else {
		$('.my_account_apply_for_return_indi_item_cont').removeClass('item_selected');
		$(this).addClass('item_selected');
	}
});

$('#my_account_apply_for_return_reason_cont .my_account_apply_for_return_indi_item_cont').removeAttr('onclick').off('click');
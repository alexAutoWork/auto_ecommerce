//$('#orders_order_page_status_select').on('click', function() {
//	$('#order_orders_page_change_status_popup').addClass('show');
//});

$(document).ready(function() {
	let value = $('select[name="status_select"]').val();
	$('select[name="status_select"]').change(function() {
		$('select[name="status_select"]').each(function() {
			let selected_value = $('select[name="status_select"]').val();
			let name = $('.global_admin_status_select_class').attr('name');
			if (name == 'status_option') {
				$('.status_option_inital').text(value)
				$('.status_change_popup').modal('show');
				$('.status_option_selected_change').text(selected_value)
			}
		});
	});
});
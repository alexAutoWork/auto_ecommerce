$('.dropdown-menu .shop_options_cont').on('click', function(e) {
			event.stopPropagation();
});

$('#account_btn_mobi').on('click', function() {
	$('.container_hide_mobi').hide();
    $('.shop_options_menu_account_cont_mobi').show();
});

$('.back_btn_mobi').on('click', function() {
    $('.shop_options_menu_account_cont_mobi').hide();
    $('.container_hide_mobi').show();
});

$('.shop_options_mobi').on('click', function() {
    if ($(this).hasClass('open')) {
        $(this).next('.dropdown_menu_mobi').slideUp();
        $(this).removeClass('open');
    }
    else {
        $(this).next('.dropdown_menu_mobi').slideDown();
        $(this).addClass('open');
    }
});

//$('button.btn.dropdown-toggle.global_option_select_1_cont').on('click', function() {
//	$(this).closest('#bs-select-1').addClass('global_option_select_1_cont_inner');
//	alert('clicked!');
//});
// JavaScript Document
$(document).ready(function() {
	$('#signup_verif_select_cont').hide();
	$('#signup_verif_code_cont').hide();
	$('#signup_details_cont').hide();
	$('#forgot_verify_select_cont').hide()
	$('#forgot_verify_mobi_associated_cont').hide()
	$('#forgot_verify_email_associated_cont').hide()
	$('#forgot_verify_code_cont').hide()
	$('#forgot_new_pw_cont').hide()
	$('#forgot_new_email_cont').hide()
	$('.signup_details_company_details').hide()
});
$('#signup_email_pw_mobile_input_submit').on('click', function() {
	// let email = $('#signup_email_input').val();
	// let password = $('#signup_pw_input').val();
	// let mobile = $('#signup_mobile_input').val();
	// $.ajaxSetup ({
	// 	headers: {
	// 		"X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
	// 	}
	// });
	// $.ajax({
	// 	url: 'validate',
	// 	method: 'POST',
	// 	data: {
	// 		'email': email,
	// 		'password': password,
	// 		'mobile': mobile,
	// 	},
	// 	dataType: 'json',
	// 	success: function (data) {
	// 		if (data.valid)
	// 	}
	// })
	$('#signup_email_pw_mobile_cont').slideUp();
	$('#signup_verif_select_cont').slideDown();
});
$('#signup_verif_select_submit').on('click', function() {
	if ($('.signup_verif_select_options').is(':checked')) {
		$('#signup_verif_select_cont').slideUp();
		$('#signup_verif_code_cont').slideDown();
	}
});
$('#signup_verif_code_submit').on('click', function() {
	$('#signup_verif_code_cont').slideUp();
	$('#signup_details_cont').slideDown();
});
$('#forgot_email_pw_select_submit').on('click', function() {
	if ($('#forgot_email_select').is(':checked')) {
		$('#forgot_email_pw_select_cont').slideUp();
		$('#forgot_verify_mobi_associated_cont').slideDown();
		$('.forgot_verify_associated_cont').addClass('shown')
		
		$('#forgot_verify_code_submit').on('click', function() {
            if ($('#forgot_verify_code_cont').hasClass('shown')) {
                $('#forgot_verify_code_cont').slideUp();
                $('#forgot_new_email_cont').slideDown();
            }
        });
	}
	if ($('#forgot_pw_select').is(':checked')) {
		$('#forgot_email_pw_select_cont').slideUp();
		$('#forgot_verify_select_cont').slideDown();
		
			$('#forgot_verify_select_submit').on('click', function() {
				if ($('#forgot_verify_sms_select').is(':checked')) {
					$('#forgot_verify_select_cont').slideUp();
					$('#forgot_verify_mobi_associated_cont').slideDown();
					$('.forgot_verify_associated_cont').addClass('shown');
				}
				if ($('#forgot_verify_email_select').is(':checked')) {
					$('#forgot_verify_select_cont').slideUp();
					$('#forgot_verify_email_associated_cont').slideDown();
					$('.forgot_verify_associated_cont').addClass('shown')
				}
			});
			
			$('#forgot_verify_code_submit').on('click', function() {
				if ($('#forgot_verify_code_cont').hasClass('shown')) {
					$('#forgot_verify_code_cont').slideUp();
					$('#forgot_new_pw_cont').slideDown();
				}
			});
	}
});

$('.forgot_verify_associated_submit').on('click', function() {
	if($('.forgot_verify_associated_cont').hasClass('shown')) {
		$('.forgot_verify_associated_cont').slideUp();
		$('#forgot_verify_code_cont').slideDown();
		$('#forgot_verify_code_cont').addClass('shown');
	}
});

$('#signup_details_company_check').click(function() {
	$('.signup_details_company_details').slideToggle(this.checked);
});
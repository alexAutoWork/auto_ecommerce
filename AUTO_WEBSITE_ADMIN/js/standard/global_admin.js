const $ = require('jquery');
const axios = require('axios');
const { get_prop_by_string } = require('../shared/shared_functions.js');

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

function button_perms_swtich(perm, pk_field=null, download_link=null) {
    let button;
    switch(perm) {
        case 'edit':
            if (pk_field !== null) {
                button = 
                `<button type="button" class="btn global_admin_remove_shadow global_admin_black_icon_btn global_admin_font_3 global_admin_table_data_sticky_icon_btns global_admin_table_data_sticky_icon_edit_icon_btn" onclick="window.location.href='${pk_field}';">`;
            }
            break;
        case 'destroy':
            if (pk_field !== null) {
                button = `<button type="button" class="btn global_admin_remove_shadow global_admin_black_icon_btn global_admin_font_3 global_admin_table_data_sticky_icon_btns global_admin_table_data_sticky_icon_destroy_icon_btn" data-pk-field='${pk_field}'><i class="fa-solid fa-trash"></i></button>`;
            }
            break;
        case 'sync':
            if (pk_field !== null) {
                button = `<button type="button" class="btn global_admin_remove_shadow global_admin_black_icon_btn global_admin_font_3 global_admin_table_data_sticky_icon_btns global_admin_table_data_sticky_icon_sync_icon_btn"><i class="fa-solid fa-arrows-rotate"></i></button>`;
            }
            break;
        case 'view':
            if (pk_field !== null) {
                button = 
                `<button type="button" class="btn global_admin_remove_shadow global_admin_black_icon_btn global_admin_font_3 global_admin_table_data_sticky_icon_btns global_admin_table_data_sticky_icon_view_icon_btn" onclick="window.location.href='${pk_field}';"><i class="fa-solid fa-eye"></i></button>`;
            }
            break;
        case 'download':
            if (download_link !== null) {
                button = 
                `<button type="button" class="btn global_admin_remove_shadow global_admin_black_icon_btn global_admin_font_3 global_admin_table_data_sticky_icon_btns global_admin_table_data_sticky_icon_download_icon_btn" onclick="window.location.href='${download_link}';" download=""><i class="fa-solid fa-file-arrow-down"></i></button>`;
            }
        default:
            button = null;
    }
    return button;
}

function load_admin_table(key, table) {
    let module_fields = [];
    let module_html_array = [];
    let table_obj = `table.${table}`;
    let perms = JSON.parse($(table_obj).data('permissions'));
	let pk_field;
	let sticky_class;
    $(`${table_obj} > thead > tr > th`).each(function() {
        table_field = $(this).data('table-field').text();
        module_fields.push(table_field);
        if ($(this).data('pk-field').text() === true) {
            pk_field = table_field;
        }
		if ($(this).data('sticky-class').text() !== undefined) {
			sticky_class = $(this).data('sticky-class').text();
		}
    });
    for (let value of key) {
        for (let obj of value) {
            let array_fields = [];
            for (let field of module_fields) {
                let obj_field = get_prop_by_string(obj, field);
                let html = `<td>${obj_field}</td>\n`;
                array_fields.push(html);
            }
            let obj_pk_field = get_prop_by_string(obj, pk_field);
            let obj_download_link = get_prop_by_string(obj, 'download_link', return_null=true);
            if (obj_download_link === undefined) {
                obj_download_link = null;
            }
            if (obj_download_link !== undefined || null) {
                // make download link here
            }
            array_fields = array_fields.toString();
            let perm_buttons = [];
            for (let perm of perms) {
                perm_buttons.push(button_perms_swtich(perm, obj_pk_field, obj_download_link));
            }
            perm_buttons = perm_buttons.toString();
            let array_html = 
            `<tr>\n
            ${array_fields}
			<td class="global_admin_table_data_sticky_icons ${sticky_class}">
            ${perm_buttons}</td>\n
            </tr>\n`;
            module_html_array.push(array_html);
        }
    }
    $(`${table_obj} > tbody`).empty().append(module_html_array);
}

function load_tables(data, tables) {
	const keys = object.keys(data);
        for (let table of tables) {
            for (let key of keys) {
                if (key.includes(table)) {
                    load_admin_table(key, table);
                }
            }
        }
}

function return_table_data(url, tables) {
	axios.get(url)
    .then((response) => {
        const module = response.data;
        load_tables(module, tables);
    })
	.catch((error) => {
		console.log(error);
	});
}

function global_load_tables(module_type, tables) {
	let url = `http://host.docker.internal:3000/admin/${module_type}`;
	return_table_data(url, tables);
}

function global_response_message(response) {
    $('#success_or_fail_popup').modal('show');
    $('success_or_fail_message').text(response.data.message);
    $('.global_admin_cancel_btn').on('click', function() {
        $('.success_or_fail_popup').modal('hide');
    })
}

$('.global_admin_table_data_sticky_icon_destroy_icon_btn').on('click', function() {
    $('#destory_popup').modal('show');
    id = $(this).data('pk-field').text();
    module_type = $(this).parent().eq(2).data('module').text();
    $('.global_admin_destory_conf_btn').on('click', function() {
        let url = `http://host.docker.internal:3000/admin/${module_type}/${id}`;
        axios.delete(url)
        .then((response) => {
            $('#destory_popup').modal('hide');
            global_response_message(response)
        })
        .catch((error) => {
            console.log(error);
        })
    })
    $('.global_admin_cancel_btn').on('click', function() {
        $('#destory_popup').modal('hide');
    })
});

exports.global_load_tables = global_load_tables;
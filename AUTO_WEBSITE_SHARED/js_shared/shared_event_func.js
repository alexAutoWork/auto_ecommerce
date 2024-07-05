const $ = require('jquery');

function toggle_element_slide(type, name=null) {
    let data_attr = 'data-page-index';
    if (name !== null) {
        data_attr = `${data_attr}-${name}`;
    }
    const current_index = $(this).closest(`[${data_attr}]`);
    let index;
    if (type === 'next') {
        index = current_index + 1;
    }
    if (type === 'back') {
        index = current_index - 1;
    }
    const current_element = current_index.attr('id');
    const element = $(this).closest(`[${data_attr}=${index}]`).attr('id');
    $(current_element).slideUp();
    $(element).slideDown();
}

export {toggle_element_slide}
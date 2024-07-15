const $ = import('jquery');
const axios = import('axios');

function url_check(url_substring) {
    let is_full = false;
    const url = window.location.toString();
    if (url.includes(url_substring)) {
        is_full = true;
    }
    return is_full;
}

function url_id(extract_param=False) {
    const url = window.location.pathname;
    const id = url.substring(url.lastIndexOf('/') + 1);
    let vals = [url, id];
    if (extract_param) {
        const param = id.split('?')[1]
        vals.push(param);
    }
    return vals;
}

function url_id_check(extract_param=False) {
    const url = url_id(extract_param);
    const params = url[0].split('/');
    const id = url[1];
    let vals;
    let is_id;
    let module;
    if (/\d/.test(id)) {
        is_id = true;
        module = params[params.length-2];
        module = module.slice(0, -1);
        vals = [is_id, module, id]
    }
    else {
        is_id = false;
        module = params[params.length-1];
        vals = [is_id, module]
    }
    if (extract_param) {
        vals.push(url[2]);
    }
    return vals;
}

function return_page() {
    const url_id_check = url_id_check();
    const is_url = url_id_check[0];
    const module = url_id_check[1];
    let funct;
    if (is_url) {
        funct = window[`get_${module}_page`]
        funct(url_id_check[2])
    }
    else {
        funct = window[`get_${module}`]
        funct()
    }
}

function return_auth_page(is_logged_in) {
    if (is_logged_in) {
        return_page();
    }
    else {
        window.location.replace = 'http://host.docker.internal:8000/login';
    }
}

function get_prop_by_string(obj, prop_string, return_null=false) {
    if (!prop_string) {
        if (return_null) {
            return null;
        }
        else {
            return obj;
        }
    }
    let props = prop_string.split('.')
    for (let i = 0, i_len = props.length - 1; i < i_len; i++) {
        let prop = props[i];
        let candi = obj[prop];
        if (candi !== undefined) {
            obj = candi;
        }
        else {
            break;
        }
        return obj[props[i]];
    }
}

export {get_prop_by_string, return_page, return_auth_page, url_id_check, url_check}
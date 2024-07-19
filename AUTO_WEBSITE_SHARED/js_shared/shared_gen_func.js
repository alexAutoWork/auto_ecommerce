const $ = import('jquery');
const axios = import('axios');
const {global} = import('../../config.js');

const gen_func = {
    get_prop: function(obj, path) {
        const prop = path.split('.');
        for (let i=0; i < prop.length; i++) {
            if (!obj) {
                return null;
            }
            obj = obj[prop[i]];
        }
        if (typeof obj === 'undefined') {
            obj = null;
        }
        return obj;
    },
    url_id: function(extract_param=false) {
        const url = window.location.pathname;
        const id = url.substring(url.lastIndexOf('/') + 1);
        let vals = [url, id];
        if (extract_param) {
            const param = id.split('?')[1]
            vals.push(param);
        }
        return vals;
    },
    url_id_check: function(extract_param=false) {
        const url = this.url_id(extract_param);
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
    },
    url_check: function(url_substring) {
        let is_full = false;
        const url = window.location.toString();
        if (url.includes(url_substring)) {
            is_full = true;
        }
        return is_full;
    },
    redirect: function(url) {
        window.location.replace = url;
    },
    render_page: function(funct_1, funct_2) {
        const url_id_attr = this.url_id_check();
        const is_url = url_id_attr[0];
        const module = url_id_attr[1];
        if (typeof funct2 !== 'undefined') {
            if (is_url) {
                funct_2(url_id_attr[2]);
            }
            else {
                funct_1();
            }
        }
        else {
            funct_1();
        }
    },
    render_user_state: function(state, functs) {
        const is_logged_in = state[0];
        const is_verified = state[1];
        let funct;
        if (is_logged_in && is_verified) {
            i = 1;
        }
        else {
            if (is_logged_in && !is_verified) {
                i = 2;
            }
            else {
                i = 3;
            }
        }
        funct = this.get_prop(functs, `funct_${i}`);
        args = this.get_prop(functs, `args_${i}`);
        if (funct !== null) {
            if (Array.isArray(args)) {
                return funct(...args);
            }
            else {
                if (args !== null) {
                    return funct(args);
                }
                return funct();
            }
        }
        return args
    },
    render_auth_page: function(state, functs) {
        inner_functs = {
            funct_1: this.render_page,
            args_1: [functs.render_1, functs.render_2],
            funct_2: this.redirect,
            args_2: [`${global.ngrok_api_url}/verify/`],
            funct_3: this.redirect,
            args_3: [`${global.ngrok_api_url}/login/`]
        }
        this.render_user_state(state, inner_functs);
    }
}

export {gen_func}
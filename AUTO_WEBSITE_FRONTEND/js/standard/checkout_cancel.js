const axios = require('axios');
const $ = require('jquery');
const {url_id_check} = import('../shared/shared_gen_func.mjs');
const {check_user} = require('./sens');

$(() => {
    [is_logged_in, withCredentials] = check_user();
    if (is_logged_in) {
        const url = url_id_check();
        const is_id = url[0];
        if (is_id) {
            const type = url[1];
            const id = url[2];
            $('.main').append(`<p class="message">if you still choose to proceed with your payment, your ${type} will still be saved...</p>`)
            const axios_url = `http://host.docker.internal:3000/auth/${id}/cancel/`;
            axios.get(axios_url, {withCredentials: withCredentials})
            .then(() => {
                console.log('success!');
            })
            .catch((err) => {
                console.log(err);
            })
    }
    }
})
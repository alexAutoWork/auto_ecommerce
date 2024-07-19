const axios = require('axios');
const {global} = require('../../config.js');

function logout() {
    axios.post(`${global.ngrok_api_url}/logout`, global.options)
    .then(() => {
        localStorage.setItem('is_logged_in', false);
        location.reload();
    })
    .catch((err) => {
        console.log(err);
    });
}

export {logout};
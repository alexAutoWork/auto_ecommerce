const axios = require('axios');

function logout(withCredentials) {
    axios.post('http://host.docker.internal:3000/logout', {withCredentials: withCredentials})
    .then(() => {
        localStorage.setItem('is_logged_in', false);
        location.reload();
    })
    .catch((err) => {
        console.log(err);
    })
}

export {logout};
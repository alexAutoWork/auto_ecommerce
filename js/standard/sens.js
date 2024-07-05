// const token_val = JSON.parse(localStorage.getItem('Token'));

// function return_token(token) {
//     if (token === null || token === undefined || token === 0) {
//         return false
//     }
//     else {
//         const token = `Token ${token_val}`;
//         const axios_auth_headers = {
//             'Content-Type': 'application/json',
//             'Authorization': token,
//         };
//         return axios_auth_headers
//     }
// };

// const token = return_token(token_val);

// exports.token = token;

// const user_id_val = JSON.parse(localStorage.getItem('UserId'));

// function return_user_id(user_id) {
//     if (user_id === null || user_id === undefined || user_id === 0) {
//         return false
//     }
//     else {
//         return user_id
//     }
// };

// const user_id = return_user_id(user_id_val);

// exports.user_id = user_id;

function check_user() {
    const is_logged_in = JSON.parse(localStorage.getItem('is_logged_in')) || false;
    let withCredentials;
    if (is_logged_in) {
        withCredentials = true;
    }
    else {
        withCredentials = false;
    }
    return [is_logged_in, withCredentials];
}

export {check_user};
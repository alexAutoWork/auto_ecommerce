function check_user() {
    const is_logged_in = JSON.parse(localStorage.getItem('is_logged_in')) || false;
    const is_verified = JSON.parse(localStorage.getItem('is_verified')) || false;
    return [is_logged_in, is_verified];
}

export {check_user};
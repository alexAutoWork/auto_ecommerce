const global = {
    ngrok_api_url: 'https://2e4b-102-68-28-61.ngrok-free.app',
    ngrok_frontend_url: 'https://08a8-102-68-28-61.ngrok-free.app',
    options: {
        withCredentials: true,
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    },
}

module.exports = {global}
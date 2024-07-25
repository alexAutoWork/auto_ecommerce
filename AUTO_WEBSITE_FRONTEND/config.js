const global = {
    ngrok_api_url: 'https://0738-102-68-28-61.ngrok-free.app',
    ngrok_frontend_url: 'https://7f72-102-68-28-61.ngrok-free.app',
    options: {
        withCredentials: true,
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    },
}

module.exports = {global}
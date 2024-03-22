const Buffer = require('buffer')

function encode(data) {
    const encoded_data = Buffer.from(data).toString('base64');
    return encoded_data
}

// function decode(encoded_data) => {
//     const decoded_data = Buffer.from(encoded_data, 'base64').toString('utf-8');
//     return decoded_data
// }

module.exports = {encode}
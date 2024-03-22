const jsdom = require('jsdom');
const fs = require('fs');
const path = require('path');

function new_otp_email(render_email_data) {
    const dom = new jsdom.JSDOM(`<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>PRODUCTS - AUTOLECTRONIX</title>
            <link rel="icon" type="image/x-icon" href="public/global_assets/logo_assets/Simplified_ver_white_border_square.png">
        </head>
        <body>
            <div class="container-fluid email_cont_1" align="center">
                <div class="container email_cont_2">
                    <h1 class="audiowide-regular email_header_1">Your OTP</h1>
                </div>
                <div class="container email_cont_3">
                    <h2 class="brandon-grotesque email_header_2">To finish creating your account, enter the otp below:</h2>
                    <h2 class="brandon-grotesque email_otp">ROEE2466</h2>
                </div>
                <div class="container roboto-light">
                    <p>If you experience any issues with your account, email the following address: <br><span class="roboto-regular">technical@autolectronix.co.za</span></p>
                    <p>Otherwise, if you didn't recently send an OTP to this email address, you can safely ignore this email</p>
                </div>
                <div class="container roboto-light-italic email_auto_respond_warning">
                    <p>This message was auto-generated, please do not respond to this email</p>
                </div>
                <div class="container email_logo">
                    <img src="public/global_assets/logo_assets/global_auto_logo_blackB_T.png" width="150px">
                </div>
            </div>
        </body>
    </html>`);

    const $ = require('jquery')(dom.window);

    $('.email_header_1').text(render_email_data.subject);
    $('.email_header_2').text(render_email_data.comment);
    $('.email_otp').text(render_email_data.otp);

    const filename = render_email_data.filename

    const content = dom.serialize()

    fs.writeFile(path.join(__dirname, `../media/html/${filename}.html`), content, (err) => {
        if (err) {
            console.log(err);
        } else {
            console.log('success!');
        }
    })
}

module.exports = {new_otp_email}
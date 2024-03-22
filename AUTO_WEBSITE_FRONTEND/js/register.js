const $ = require('jquery')
const axios = require('axios')
// const pug = require('pug');
// const express = require('express');
// const encode = require('../encode')

// app.use(express.json());

$('#signup_email_pw_mobile_input_submit').on('click', function() {
    // app.post('http://localhost:8000/register', (req, res) => {
    //     res.json(data);
    // });
    console.log('clicked!!!')
    let email = $('#signup_email_input').val()
    let password = $('#signup_pw_input').val()
    let mobile_no = $('#signup_mobile_input').val()
    let user_data = {'email': email, 'password': password, 'mobile_no': mobile_no}
    user_data = JSON.stringify(user_data)
    console.log(user_data)
    axios.post('http://localhost:8000/register', user_data, {
        headers: {'Content-Type': 'application/json'}})
    .then((response) => {
        console.log(response)
    })
    .catch((error) => {
        console.log(error.response.data)
    })
})
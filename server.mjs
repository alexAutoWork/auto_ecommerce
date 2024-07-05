// import express from 'express';
// import path from 'path';
// import { fileURLToPath } from 'url';
// import fs from 'fs';

// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);


// return result;

// fs.readdir(folderpath, (err, fileNames) => {
//     fileNames.forEach(filename => {
//         const filenameurl = path.parse(filename).name;
//         const filepath = path.resolve(folderpath, filename);

//         result = [filenameurl, filepath];
//         return true;
//     });
// });

// function returnfolderurl(filenameurl, filepath) {

//     app.get(`/${filenameurl}`, (req, res, next) => {
//         const _retfile = path.join(__dirname, filepath);
    
//         res.sendFile(_retfile);
//     });
// }

// var folder1oripath = './html/auth/'

// var app = express();

// app.listen(3000, () => {
//     console.log('Server is running on port 3000');
//     var readfolder1 = readfolder(folder1oripath);
//     console.log(readfolder1);
//     var folder1url = readfolder1[0];
//     var folder1path = readfolder1[1];
//     returnfolderurl(folder1url, folder1path);
// });



// function loadhtml(folderpath) {

//     function readfolder(folderpath) {
//         fs.readdir(folderpath, (err, fileNames) => {
//             fileNames.forEach(filename => {
//                 const filenameurl = path.parse(filename).name;
//                 const filepath = path.resolve(dir, filename);
//                 return filenameurl, filepath;
//             });
//         });
//     };

    // app.get(`/${filenameurl}`, (req, res, next) => {
    //     const _retfile = path.join(__dirname, filepath);
    
    //     res.sendFile(_retfile);
    // });

// };

// const app = express();

// app.use('/public', express.static('js'));
// app.use('/public', express.static('images'));
// app.use('/public', express.static('css'));
// app.use('/public', express.static('node_modules/bootstrap/dist/css'));
// app.use('/public', express.static('node_modules/bootstrap/dist/js'));
// app.use('/public', express.static('node_modules/jquery/dist'));
// app.use('/public', express.static('node_modules/popper.js/dist'));
// app.use('/public', express.static('node_modules/@fortawesome/fontawesome-free/css'))
// app.use('/public', express.static('node_modules/@fortawesome/fontawesome-free/js'))
// app.use('/js', express.static(path.join(__dirname, '/node_modules/jquery/dist')));
// app.use('/js', express.static(path.join(__dirname, '/node_modules/popper.js/dist')));
// app.use('/js', express.static(path.join(__dirname, '/node_modules/@fortawesome/fontawesome-common-types')));
// app.use('/js', express.static(path.join(__dirname, '/node_modules/@fortawesome/fontawesome-svg-core')));
// app.use('/js', express.static(path.join(__dirname, '/node_modules/@fortawesome/free-brands-svg-icons')));
// app.use('/js', express.static(path.join(__dirname, '/node_modules/@fortawesome/free-regular-svg-icons')));
// app.use('/js', express.static(path.join(__dirname, '/node_modules/@fortawesome/free-solid-svg-icons')));


// app.get('/products', (req, res) => {
//     const _retfile = path.join(__dirname, './html/standard/products.html');

//     res.sendFile(_retfile);
// });

// app.listen(3000, () => {
//     console.log('Listening on port ' + 3000);
// });

// app.get(filename, (req, res, next) => {

// });

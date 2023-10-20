
const net = require('net');


const inputServer = net.createServer((socket) => {
    console.log('new client from ',socket.remoteAddress);

    socket.on('data', onData);
    socket.once('close', onClose);
    socket.on('error', onError);

    socket.write('hello from the server!\r\n');

    function onData(d) {  
        console.log('DATA IN:',String(d));
    }
    function onClose() {
        console.log('input connection from %s closed', socket.remoteAddress);  
    }
    function onError(err) {  
        console.log('input Connection %s error: %s', socket.remoteAddress, err.message);  
    }  
});

inputServer.listen(3002, () => console.log('server listening to ',inputServer.address()) );
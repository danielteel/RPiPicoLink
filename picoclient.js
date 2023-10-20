const { WiFi } = require('wifi');
const wifi = new WiFi();

const { Button } = require('button');


wifi.connect({ ssid: 'Pico', password: '12345678' }, (err) => {
  if (err) {
    console.log('couldnt connect to wifi',err);
  } else {

    const { PicoCYW43 } = require('pico_cyw43');
    const pico_cyw43 = new PicoCYW43();
    
    // Blink the Pico-W's on-board LED
    setInterval(() => {
      if (pico_cyw43.getGpio(0)) {
        pico_cyw43.putGpio(0, false); // turn-off LED
      } else {
        pico_cyw43.putGpio(0, true); // turn-on LED
      }
    }, 1000);

      const net = require('net');
      const btn = new Button(0);

      var client = net.createConnection({ host: '10.42.0.1', port: 3002 }, () => {
        // 'connect' listener.
        console.log('Connected to server');
        client.write('hello from the client!');

        btn.on('click', function () {
          client.write('button pressed');
        });

      });
      client.on('data', (data) => {
        console.log('DATA IN:',data);
      });
      client.on('end', () => {
        console.log('disconnected from server');
      });
      client.on('close', () => {
        console.log('disconnected from server');
        btn.close();
      });
      client.on('error', (err) => {
        console.log('error', err);
      });
  }
});
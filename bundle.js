/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ([
/* 0 */,
/* 1 */
/***/ ((module) => {

"use strict";
module.exports = require("wifi");

/***/ }),
/* 2 */
/***/ ((module) => {

"use strict";
module.exports = require("button");

/***/ }),
/* 3 */
/***/ ((module) => {

"use strict";
module.exports = require("pico_cyw43");

/***/ }),
/* 4 */
/***/ ((module) => {

"use strict";
module.exports = require("net");

/***/ })
/******/ 	]);
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
const { WiFi } = __webpack_require__(1);
const wifi = new WiFi();

const { Button } = __webpack_require__(2);


wifi.connect({ ssid: 'Pico', password: '12345678' }, (err) => {
  if (err) {
    console.log('couldnt connect to wifi',err);
  } else {

    const { PicoCYW43 } = __webpack_require__(3);
    const pico_cyw43 = new PicoCYW43();
    
    // Blink the Pico-W's on-board LED
    setInterval(() => {
      if (pico_cyw43.getGpio(0)) {
        pico_cyw43.putGpio(0, false); // turn-off LED
      } else {
        pico_cyw43.putGpio(0, true); // turn-on LED
      }
    }, 1000);

      const net = __webpack_require__(4);
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
})();

/******/ })()
;
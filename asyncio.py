import network
import socket
import time
import gc
import asyncio
import sys

from machine import ADC
from machine import Pin
from machine import Timer


def getTemp():
    adc = ADC(4) 
    ADC_voltage = adc.read_u16() * (3.3 / 65536.0)
    temperature_celcius = 27.0 - (ADC_voltage - 0.706)/0.001721
    return 32.0+1.8*temperature_celcius


STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_GOT_IP = 3
STAT_CONNECT_FAIL = -1
STAT_NO_AP_FOUND = -2
STAT_WRONGPASSWORD = -3

STATE_NEW = 0
STATE_LISTENING = 1
STATE_CONNECTING = 2
STATE_CONNECTED = 3
STATE_PEER_CLOSED = 4
STATE_ACTIVE_UDP = 5


    #define STATE_NEW 0
    #define STATE_LISTENING 1
    #define STATE_CONNECTING 2
    #define STATE_CONNECTED 3
    #define STATE_PEER_CLOSED 4
    #define STATE_ACTIVE_UDP 5
    # 0,                /* ERR_OK          0      No error, everything OK  */
    # MP_ENOMEM,        /* ERR_MEM        -1      Out of memory error      */
    # MP_ENOBUFS,       /* ERR_BUF        -2      Buffer error             */
    # MP_EWOULDBLOCK,   /* ERR_TIMEOUT    -3      Timeout                  */
    # MP_EHOSTUNREACH,  /* ERR_RTE        -4      Routing problem          */
    # MP_EINPROGRESS,   /* ERR_INPROGRESS -5      Operation in progress    */
    # MP_EINVAL,        /* ERR_VAL        -6      Illegal value            */
    # MP_EWOULDBLOCK,   /* ERR_WOULDBLOCK -7      Operation would block    */
    # MP_EADDRINUSE,    /* ERR_USE        -8      Address in use           */
    # MP_EALREADY,      /* ERR_ALREADY    -9      Already connecting       */
    # MP_EALREADY,      /* ERR_ISCONN     -10     Conn already established */
    # MP_ENOTCONN,      /* ERR_CONN       -11     Not connected            */
    # -1,               /* ERR_IF         -12     Low-level netif error    */
    # MP_ECONNABORTED,  /* ERR_ABRT       -13     Connection aborted       */
    # MP_ECONNRESET,    /* ERR_RST        -14     Connection reset         */
    # MP_ENOTCONN,      /* ERR_CLSD       -15     Connection closed        */
    # MP_EIO,           /* ERR_ARG        -16     Illegal argument.        */
    # MP_EBADF,         /* _ERR_BADF      -17     Closed socket (null pcb) */

wlan=None
async def connect(ssid, password, ipAddress, port):
    global wlan
    wlanConnectTime=0
    wlanConnectTimeout=10
    wlan=network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(True)
    wlan.connect(ssid, password)

    sock = None
    try:
        sockAddress = socket.getaddrinfo(ipAddress, port)[0][-1]
    except OSError:
        return

    while 1:
        while wlan.status()!=STAT_GOT_IP:
            if wlanConnectTime>wlanConnectTimeout:
                wlan.disconnect()
                wlan.connect(ssid, password)
                wlanConnectTime=0
            print('DanNet: trying to establish WiFi connection', wlanConnectTime)
            await asyncio.sleep(0.5)
            wlanConnectTime+=0.5

        wlanConnectTime=0
        
        while wlan.status()==STAT_GOT_IP:

            sock=socket.socket()
            print(sock)       
            
            await asyncio.sleep(1)
            try:
                sock.connect(sockAddress)
                while wlan.status()==STAT_GOT_IP and str(sock)[:15]=='<socket state=3':
                    temp = getTemp()
                    print(gc.mem_free(), temp)
                    sock.write(str(temp).encode())
                    await asyncio.sleep_ms(100)

                raise OSError('connection lost')

            except OSError as err:
                print(err)
                sock.close()
                sock=None



async def main():
    while 1:
        await connect('Pico', '123456789', '10.42.0.1', 80)


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
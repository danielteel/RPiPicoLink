import network
import socket
import asyncio
import parse
import gc
import machine
import time

led=machine.Pin('LED')
led.value(1)
time.sleep(2)
led.value(0)

# STAT_IDLE = 0
# STAT_CONNECTING = 1
STAT_GOT_IP = 3
# STAT_CONNECT_FAIL = -1
# STAT_NO_AP_FOUND = -2
# STAT_WRONGPASSWORD = -3

# STATE_NEW = 0
# STATE_LISTENING = 1
# STATE_CONNECTING = 2
# STATE_CONNECTED = 3
# STATE_PEER_CLOSED = 4
# STATE_ACTIVE_UDP = 5



async def connect(ssid, password, ipAddress, port):
    class SockError(Exception): pass
    wlanConnectTime=0
    wlanConnectTimeout=10
    wlanTimeouts=0
    wlanMaxTimeouts=3

    wlan=network.WLAN(network.STA_IF)
    wlan.config(pm = network.WLAN.PM_NONE)
    wlan.config(txpower=1000)
    while (wlan.config('pm')!=network.WLAN.PM_NONE):
        await asyncio.sleep_ms(10)
    wlan.disconnect()
    wlan.active(True)
    wlan.connect(ssid, password)
    print(wlan.config('txpower'))

    sock = None
    try:
        sockAddress = socket.getaddrinfo(ipAddress, port)[0][-1]
    except OSError:
        return


    while 1:
        while wlan.status()!=STAT_GOT_IP:
            if wlanConnectTime>wlanConnectTimeout:
                wlan.disconnect()
                wlan.active(False)
                await asyncio.sleep_ms(250)
                wlan.active(True)
                wlan.connect(ssid, password)
                wlanConnectTime=0
                wlanTimeouts+=1
                if wlanTimeouts>=wlanMaxTimeouts:
                    machine.WDT(0, 1)
                    pass
            await asyncio.sleep_ms(250)
            wlanConnectTime+=0.25

        wlanConnectTime=0
        wlanTimeouts=0
        
        while wlan.status()==STAT_GOT_IP:

            sock=socket.socket()   
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            await asyncio.sleep_ms(250)
            try:
                try:
                    sock.connect(sockAddress)
                except OSError as err:
                    if err.errno!=104:#ECONNRESET
                        raise err
                
                if wlan.status()==STAT_GOT_IP and str(sock)[:15].encode()==b'<socket state=3':
                    sock.write('initial rssi='+str(wlan.status('rssi'))+'\n')

                while wlan.status()==STAT_GOT_IP and str(sock)[:15].encode()==b'<socket state=3':
                    recvData=b''
                    while str(sock)[:15].encode()==b'<socket state=3' and ('incoming=0 ' not in str(sock)):
                        byte=sock.recv(1)
                        if byte==b'\n':
                            sock.write('rssi='+str(wlan.status('rssi'))+' recvd='+str(parse.compile(recvData))+'\n')
                            recvData=b''
                        else:
                            recvData = recvData + byte
                    await asyncio.sleep_ms(0)

                raise SockError('connection lost')

            except SockError as err:
                sock.close()
                sock=None


async def main():
    while 1:
        await connect('Pico', '123456789', '10.42.0.1', 80)


try:
    asyncio.run(main())
except Exception as err:
    print(err)
finally:
    asyncio.new_event_loop()
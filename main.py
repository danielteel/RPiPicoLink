import network
import socket
import asyncio
import parse
import gc
import machine
import time
import mlx90614
from machine import I2C, Pin, UART

#uart = UART(0, baudrate = 4800, rx=Pin(1), timeout=1)

#i2c = I2C(id=0, sda = Pin(4), scl = Pin(5), freq=100000)
#sensor = mlx90614.MLX90614(i2c)

led=machine.Pin('LED')
led.value(1)
time.sleep_ms(2000)
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

def recieved(wlan, sock, message):
    sentence=uart.readline()
    if not sentence or sentence[:6]!=b'$GPGGA':
        sentence=b''
    else:
        print(sentence)
    sock.write('temp='+str(sensor.read_object_temp())+' rssi='+str(wlan.status('rssi'))+' '+sentence.decode()+'\n')


async def connect(ssid, password, ipAddress, port, onConnect, onDisconnect, onRecieve):
    class SockError(Exception): pass
    wlanConnectTime=0
    wlanConnectTimeout=10
    wlanTimeouts=0
    wlanMaxTimeouts=3

    wlan=network.WLAN(network.STA_IF)
    wlan.config(pm = network.WLAN.PM_NONE)
    wlan.config(txpower=40)
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
                    if err.errno!=104 and err.errno!=113 and err.errno!=105 and err.errno!=103:#ECONNRESET or EHOSTUNREACH or ECONNABORTED
                        raise err
                    else:
                        raise SockError('failed')

                recvData=b''
                
                if wlan.status()==STAT_GOT_IP and str(sock)[:15]=='<socket state=3':
                    onConnect(sock)

                    while wlan.status()==STAT_GOT_IP and str(sock)[:15].encode()==b'<socket state=3':

                        while str(sock)[:15]=='<socket state=3' and ('incoming=0 ' not in str(sock)):
                            recvData+=sock.recv(64)

                        while recvData:
                            newLinePos = recvData.find(b'\n')
                            if newLinePos!=-1:
                                onRecieve(sock, recvData[:newLinePos+1])
                                recvData=recvData[newLinePos+1:]
                            else:
                                break

                        await asyncio.sleep_ms(5)

                raise SockError('connection lost')

            except SockError as err:
                if err.value!='failed':
                    onDisconnect()
                print("Error on socket:", err)
                sock.close()
                sock=None
                
            except KeyboardInterrupt as err:
                onDisconnect()
                sock.close()
                sock=None
                raise err
            except:
                onDisconnect()
                print("Uncaught exception")
                sock.close()
                sock=None
                raise


theSocket=None
def onConnect(sock):
    global theSocket
    theSocket=sock
    sock.write('hi\n')
    print('onConnect', sock)

def onDisconnect():
    global theSocket
    theSocket=None
    print('onDisconnect')

def onRecieve(sock, message):
    print('onRecieve', sock, message)
    sock.write('thanks\n')


async def main():
    while 1:
        await connect('Pico', '123456789', '10.42.0.1', 80, onConnect, onDisconnect, onRecieve)


try:
    asyncio.run(main())
except Exception as err:
    print(err)
finally:
    asyncio.new_event_loop()
import network
import socket
import time
import micropython
import gc

from machine import ADC
from machine import Pin
from machine import Timer

STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_GOT_IP = 3
STAT_CONNECT_FAIL = -1
STAT_NO_AP_FOUND = -2
STAT_WRONGPASSWORD = -3

class DanNet:
    instance=None

    active=False
    timer=None
    wlan=None

    ssid=None
    password=None

    wlanConnectTime=0
    wlanConnectTimeout=10
    wlanConnectTimerPeriod=2

    socketAddress=None
    socket=None
    isConnected=False

    def __new__(cls):
        if cls.instance is None:
            cls.instance=object.__new__(cls)
        return cls.instance
    
    def shutdown(self):
        this=self.__class__
        this.active=False
        this.isConnected=False
        if this.socket:
            try:
                this.socket.close()
            finally:
                this.socket=None

        if this.wlan:
            this.wlan.disconnect()
            this.wlan.active(False)
        if this.timer:
            this.timer.deinit()
            this.timer=None
    
    def startup(self, ssid, password, ipAddress, port):
        this = self.__class__

        if this.active:
            self.shutdown()
        
        this.ssid=ssid
        this.password=password
        this.socketAddress=socket.getaddrinfo(ipAddress, port)[0][-1]
        this.isConnected=False

        this.wlan=network.WLAN(network.STA_IF)
        this.wlan.disconnect()
        this.wlan.active(True)
        this.wlan.connect(this.ssid, this.password)

        this.active=True

        this.timer = Timer(period=this.wlanConnectTimerPeriod*1000, mode=Timer.PERIODIC, callback=this.instance.tick)

    def tick(self, t):
        this=self.__class__
        if not this.active:
            return
        
        if this.wlan.status()!=STAT_GOT_IP:
            this.wlanConnectTime+=this.wlanConnectTimerPeriod
            if this.wlanConnectTime>this.wlanConnectTimeout:
                this.wlan.disconnect()
                this.wlan.connect(this.ssid, this.password)
                this.wlanConnectTime=0
            print('DanNet: trying to establish WiFi connection', this.wlanConnectTime)
        else:
            this.wlanConnectTime=0
            
            if this.socket is None:
                try:
                    this.socket=socket.socket()
                    this.socket.connect(this.socketAddress)
                    
        

    def get(self):
        this=self.__class__
        if this.wlan.isconnected():
            s=socket.socket()
            ai=socket.getaddrinfo('10.42.0.1', 80)[0][-1]
            try:
                
                adc = ADC(4) 
                ADC_voltage = adc.read_u16() * (3.3 / (65536))
                temperature_celcius = 27 - (ADC_voltage - 0.706)/0.001721
                temp_fahrenheit=32+(1.8*temperature_celcius)
                s.connect(ai)
                s.send(str.encode(str(temp_fahrenheit)))
            finally:
                s.close()

try:
    DanNet().startup('Pico', '123456789', '10.42.0.1', 80)
    DanNet().startup('Pico', '123456789', '10.42.0.1', 80)

    while True:
        gc.collect()
        time.sleep(1)

except KeyboardInterrupt:
    DanNet().shutdown()
from mqtt_as import MQTTClient, config
import asyncio
import mlx90614
from machine import I2C, Pin

# Local configuration
config['ssid'] = 'Pico'  # Optional on ESP8266
config['wifi_pw'] = '123456789'
config['server'] = '10.42.0.1'  # Change to suit e.g. 'iot.eclipse.org'
config["queue_len"] = 1  # Use event interface with default queue size

async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        print((topic, msg, retained))

async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe('foo_topic', 1)  # renew subscriptions

async def main(client):
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))

    i2c = I2C(id=0, sda = Pin(4), scl = Pin(5), freq=100000)
    sensor = mlx90614.MLX90614(i2c)
    while True:
        await asyncio.sleep_ms(1000)
        temp=sensor.read_object_temp()*1.8+32
        print('publish', temp)
        # If WiFi is down the following will pause for the duration.
        await client.publish('temp', '{}'.format(temp), qos = 1)

#MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    asyncio.new_event_loop()
    client.close()  # Prevent LmacRxBlk:1 errors
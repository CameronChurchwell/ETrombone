import asyncio
import sys
# from itertools import count, takewhile
# from typing import Iterator

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


async def uart(rx_handler):
    """Simple UART service
    """

    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        if device.name == 'w':
            if UART_SERVICE_UUID.lower() in adv.service_uuids:
                return True

        return False

    device = await BleakScanner.find_device_by_filter(match_nus_uuid)

    if device is None:
        print("no matching device found, you may need to edit match_nus_uuid().")
        sys.exit(1)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    # def handle_rx(_: BleakGATTCharacteristic, data: bytearray):
    #     print("received:", data)


    print('trying to connect')
    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        # await client.start_notify(UART_TX_CHAR_UUID, handle_rx)
        await client.start_notify(UART_TX_CHAR_UUID, rx_handler)
        print('connected')
        while client.is_connected:
            await asyncio.sleep(1)
        # nus = client.services.get_service(UART_SERVICE_UUID)
        # rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)
        # while True:
        #     data = await loop.run_in_executor(None, sys.stdin.buffer.readline)

if __name__ == "__main__":
    def handler(_: BleakGATTCharacteristic, data: bytearray):
        print(data)
    try:
        asyncio.run(uart(handler))
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
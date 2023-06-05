_author__ = "Patrice Guyot"

"""
***********************************************************************
Name            : yin.py
Description     : Fundamental frequency estimation. Based on the YIN alorgorithm [1]: De Cheveigné, A., & Kawahara, H. (2002). YIN, a fundamental frequency estimator for speech and music. The Journal of the Acoustical Society of America, 111(4), 1917-1930.
Author          : Patrice Guyot. Previous works on the implementation of the YIN algorithm have been made thanks to Robin Larvor, Maxime Le Coz and Lionel Koenig.
***********************************************************************
"""


from ulab import numpy as np
import uasyncio as asyncio
from bluetooth import BLE
from bleuart import BLEUART


class ThreadSafeQueue:  # MicroPython optimised
    def __init__(self, buf):
        self._q = [0 for _ in range(buf)] if isinstance(buf, int) else buf
        self._size = len(buf)
        self._wi = 0
        self._ri = 0
        self._evput = asyncio.ThreadSafeFlag()  # Triggered by put, tested by get
        self._evget = asyncio.ThreadSafeFlag()  # Triggered by get, tested by put

    def full(self):
        return ((self._wi + 1) % self._size) == self._ri

    def empty(self):
        return self._ri == self._wi

    def qsize(self):
        return (self._wi - self._ri) % self._size

    def get_sync(self, block=False):  # Remove and return an item from the queue.
        if not block and self.empty():
            raise IndexError  # Not allowed to block
        while self.empty():  # Block until an item appears
            pass
        r = self._q[self._ri]
        self._ri = (self._ri + 1) % self._size
        self._evget.set()
        return r

    def put_sync(self, v, block=False):
        self._q[self._wi] = v
        self._evput.set()  # Schedule task waiting on get
        if not block and self.full():
            raise IndexError
        while self.full():
            pass  # can't bump ._wi until an item is removed
        self._wi = (self._wi + 1) % self._size

    async def put(self, val):  # Usage: await queue.put(item)
        while self.full():  # Queue full
            await self._evget.wait()
        self.put_sync(val)

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.get()

    async def get(self):
        while self.empty():
            await self._evput.wait()
        r = self._q[self._ri]
        self._ri = (self._ri + 1) % self._size
        self._evget.set()  # Schedule task waiting on ._evget
        return r

    async def get_into_array(self, ndarray):
        while self.empty():
            await self._evput.wait()
        num = len(ndarray)
        for i in range(0, num):
            ndarray[i] = self._q[self._ri]
            self._ri = (self._ri + 1) % self._size
        self._evget.set()  # Schedule task waiting on ._evget

    async def get_as_array(self, count: int):
        while self.empty():
            await self._evput.wait()
        size = min(self._size-self._ri, count)
        first_block = np.frombuffer(self._q, count=size, dtype=np.uint16, offset=2*self._ri)
        second_block = np.frombuffer(self._q, count=count-size, dtype=np.uint16, offset=0) if size < count else np.array([], dtype=np.uint16)
        self._ri = (self._ri + count) % self._size
        self._evget.set()  # Schedule task waiting on ._evget
        return np.concatenate((first_block, second_block))


if __name__ == '__main__':
    print('starting pitch detector...')

    from machine import Pin, ADC, Timer
    import array
    import uasyncio as asyncio

    adc = ADC(Pin(28))
    timer = Timer(-1)

    #setup bluetooth
    ble = BLE()
    uart = BLEUART(ble)

    def on_rx(*args):
        print(args)
        print("rx: ", uart.read().decode().strip())

    uart.irq(handler=on_rx)

    # TIME AND RATE CONSTANTS
    window_size = 512
    buffer_size = window_size*2
    sample_rate = 8192
    scaler = sample_rate / window_size
    cutoff = int(500 // scaler)

    buffer = array.array("H")
    for i in range(0, buffer_size):
        buffer.append(0)

    tsq = ThreadSafeQueue(buffer)

    def isr(_):  # Interrupt handler
        tsq.put_sync(adc.read_u16())  # Put ADC value on queue
    timer.init(freq=sample_rate, mode=Timer.PERIODIC, callback=isr)

    async def run():
        global tsq
        global uart
        playing = False
        print("startup complete")
        while True:
            if tsq.qsize() >= window_size:
                window = await tsq.get_as_array(window_size)
                real, imag = np.fft.fft(window)
                power_spectrogram = (real * real) + (imag * imag)
                max_idx = np.argmax(power_spectrogram[1:cutoff]) + 1
                max_power = power_spectrogram[max_idx]
                # not scaled relative to anything meaningful
                max_db = 10*np.log10(max_power/np.median(power_spectrogram))
                if max_db >= 20:
                    playing = True
                    freq = max_idx * scaler
                    uart.write(str(freq) + '\n')
                    print(freq, max_db)
                else:
                    if playing:
                        uart.write(str(0) + '\n')
                        playing = False

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print('stopping!')
    except Exception as e:
        raise e
    finally:
        timer.deinit()
        uart.close()
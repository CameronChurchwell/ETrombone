from pydub import AudioSegment
from pydub.playback import play
import serial

a440 = AudioSegment.from_wav('./a440.wav')
print('ready')

with serial.Serial('/dev/tty.usbmodem142101') as usb:
    while True:
        if usb.in_waiting >= 3:
            line = usb.readline()
            value = int(line.decode('utf-8')[0])
            if value:
                play(a440)

from pedalboard import Pedalboard, Chorus, Compressor, Delay, Gain, Reverb, Phaser
from pedalboard.io import AudioStream

# Open up an audio stream:
with AudioStream(
    input_device_name="MacBook Pro Microphone",  # Guitar interface
    output_device_name="MacBook Pro Speakers",
    allow_feedback=True
) as stream:
    # Audio is now streaming through this pedalboard and out of your speakers!
    stream.plugins = Pedalboard([
        Compressor(threshold_db=-50, ratio=25),
        Gain(gain_db=30),
        Chorus(),
        Phaser(),
        Reverb(room_size=0.25),
    ])
    while True:
        try:
            reverb = input("enter reverb value [0-1]: ")
            stream.plugins = Pedalboard([
                Compressor(threshold_db=-50, ratio=25),
                Gain(gain_db=30),
                Chorus(),
                Phaser(),
                Reverb(room_size=float(reverb)),
            ])
        except KeyboardInterrupt:
            print('done!')
            break

# import serial
# with serial.Serial('/dev/tty.usbmodem142101') as usb:
#     while True:
#         if usb.in_waiting >= 3:
#             line = usb.readline()
#             value = int(line.decode('utf-8')[0])
#             if value:
#                 play(a440)

# The live AudioStream is now closed, and audio has stopped.

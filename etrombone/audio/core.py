"""
Core audio processing file
"""

from pedalboard import Pedalboard, Chorus, Compressor, Delay, Gain, Reverb, Phaser
from pedalboard._pedalboard import load_plugin
from pedalboard.io import AudioStream
from pathlib import Path

audio_dir = Path(__file__).parent

brass_path = audio_dir / 'assets' / 'Aeternus Brass.vst3'
brass = load_plugin(str(brass_path))

# Open up an audio stream:
with AudioStream(
    input_device_name="MacBook Pro Microphone",  # Guitar interface
    output_device_name="MacBook Pro Speakers",
    allow_feedback=True
) as stream:
    # Audio is now streaming through this pedalboard and out of your speakers!
    while True:
        try:
            # reverb = input("enter reverb value [0-1]: ")
            stream.plugins = Pedalboard([
                # Compressor(threshold_db=-50, ratio=25),
                # Gain(gain_db=30),
                # Chorus(),
                # Phaser(),
                # Reverb(room_size=float(reverb)),
                brass
            ])
        except KeyboardInterrupt:
            print('done!')
            break


# Code for working with serial input (one button instrument)
# import serial
# with serial.Serial('/dev/tty.usbmodem142101') as usb:
#     while True:
#         if usb.in_waiting >= 3:
#             line = usb.readline()
#             value = int(line.decode('utf-8')[0])
#             if value:
#                 play(a440)

# The live AudioStream is now closed, and audio has stopped.

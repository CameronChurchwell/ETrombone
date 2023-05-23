"""
Core audio processing file
"""

from pedalboard import Pedalboard, Chorus, Compressor, Delay, Gain, Reverb, Phaser
from pedalboard._pedalboard import load_plugin
from etrombone.inputs import getControllerPosition
from pedalboard.io import AudioStream
from pathlib import Path
import numpy as np

audio_assets_dir = Path(__file__).parent / 'assets'
plugin = load_plugin(str(audio_assets_dir / 'bbc.vst3'))
plugin.show_editor()

gen = getControllerPosition()
initial_position = next(gen)

states = [False] * 100
with AudioStream(
    input_device_name="Microphone (Yeti Nano)",
    output_device_name="Speakers (FiiO Q series)",
    allow_feedback=True,
    buffer_size=16000
) as stream:
    stream.plugins = Pedalboard([
        plugin,
        # Reverb(room_size=0.25),
    ])
    while True:
        input("hit enter to trigger note")
        current_position = next(gen)
        distance = np.linalg.norm(current_position-initial_position)
        print(distance)
        if distance < 0.5:
            note = 69
        else:
            note = 70
        print(note)
        if states[note]: #playing
            print(plugin.midi_note_off(noteNumber=note, sampleNumber=1))
            states[note] = not states[note]
        else:
            print(plugin.midi_note_on(noteNumber=note, sampleNumber=1))
            states[note] = not states[note]
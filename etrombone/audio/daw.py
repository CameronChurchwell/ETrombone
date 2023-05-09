import dawdreamer as daw
from pathlib import Path
BUFFER_SIZE = 128 # Parameters will undergo automation at this buffer/block size.
PPQN = 960 # Pulses per quarter note.
audio_dir = Path(__file__).parent

brass_path = audio_dir / 'assets' / 'Aeternus Brass.vst3'
# brass_path = audio_dir / 'assets' / 'DSK Brass.dll'
SYNTH_PLUGIN = str(brass_path)
SAMPLE_RATE = 44100


engine = daw.RenderEngine(SAMPLE_RATE, BUFFER_SIZE)

# Make a processor and give it the unique name "my_synth", which we use later.
synth = engine.make_plugin_processor("Aeternus Brass", SYNTH_PLUGIN)
# assert synth.get_name() == "my_synth"

# # Plugins can show their UI.
# synth.open_editor()  # Open the editor, make changes, and close
# synth.save_state('C:/path/to/state1')
# # Next time, we can load_state without using open_editor.
# synth.load_state('C:/path/to/state1')

# # For some plugins, it's possible to load presets:
# synth.load_preset('C:/path/to/preset.fxp')
# synth.load_vst3_preset('C:/path/to/preset.vstpreset')

# # We'll set automation for our synth. Later we'll want to bake this automation into
# # audio-rate data, so we must enable `record_automation`. If you don't intend to call
# # `get_automation()` later, there's no need to do this:
# synth.record_automation = True

# # Get a list of dictionaries where each dictionary describes a controllable parameter.
# print(synth.get_parameters_description()) 
# print(synth.get_parameter_name(1)) # For Serum, returns "A Pan" (oscillator A's panning)

# # Note that Plugin Processor parameters are between [0, 1], even "discrete" parameters.
# # We can simply set a constant value.
# synth.set_parameter(1, 0.1234)
# # The Plugin Processor can set automation with data at audio rate.
# num_seconds = 10
# synth.set_automation(1, 0.5+.5*make_sine(.5, num_seconds)) # 0.5 Hz sine wave remapped to [0, 1]

# # It's also possible to set automation in alignment with the tempo.
# # Let's make a numpy array whose "sample rate" is PPQN. Suppose PPQN is 960.
# # Each 960 values in the array correspond to a quarter note of time progressing.
# # Let's make a parameter alternate between 0.25 and 0.75 four times per beat.
# # Here, the second argument to `make_sine` actually represents a number of beats.
# num_beats = 20
# automation = make_sine(4, num_beats, sr=PPQN)
# automation = 0.25+.5*(automation > 0).astype(np.float32)
# synth.set_automation(1, automation, ppqn=PPQN)

# # Load a MIDI file and convert the timing to absolute seconds (beats=False).
# # Changes to the Render Engine's BPM won't affect the timing. The kwargs below are defaults.
# synth.load_midi(MIDI_PATH, clear_previous=True, beats=False, all_events=True)

# # Load a MIDI file and keep the timing in units of beats. Changes to the Render Engine's BPM
# # will affect the timing.
# synth.load_midi(MIDI_PATH, beats=True)

# # We can also add one note at a time, specifying a start time and duration, both in seconds
# synth.add_midi_note(60, 127, 0.5, .25) # (MIDI note, velocity, start, duration)

# # With `beats=True`, we can use beats as the unit for the start time and duration.
# # Rest for a beat and then play a note for a half beat.
# synth.add_midi_note(67, 127, 1, .5, beats=True)

# # For any processor type, we can get the number of inputs and outputs
# print("synth num inputs: ", synth.get_num_input_channels())
# print("synth num outputs: ", synth.get_num_output_channels())

# reverb_processor = engine.make_plugin_processor("reverb", REVERB_PLUGIN)

# graph = [
#   (synth, []),  # synth takes no inputs, so we give an empty list.
#   (reverb_processor, [synth.get_name()])  # hard-coding "my_synth" also works instead of get_name()
# ]

# engine.load_graph(graph)
# engine.render(5)  # Render 5 seconds of audio.
# # engine.render(5, beats=True)  # Render 5 beats of audio.

# # You can modify processors without recreating the graph.
# synth.load("C:/path/to/other_preset.fxp")

# # After rendering, you can fetch PPQN-rate automation that has been baked into audio-rate data.
# # Use a smaller buffer size to get more granularity in this data, otherwise there will be
# # some "steppiness"/"nearest-lookup".
# all_automation = synth.get_automation()  # a dictionary of all parameters at audio-rate.

# # After rendering, you can save to MIDI with absolute times, in case the BPM affected it.
# synth.save_midi("my_midi_output.mid")

# # Even after a render, we can still modify our processors and re-render the graph.
# # All of our MIDI is still loaded.
# synth.load_preset("C:/path/to/other_preset.fxp")
# engine.render(DURATION)

# synth.clear_midi()
# synth.add_midi_note(65, 100, 1, .5, beats=True)

# # continue rendering...
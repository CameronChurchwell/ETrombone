# ETrombone

An electronic trombone implemented in Python and with support for multiple different hardware systems

## Installation

Requires a recent version of Python. From the main directory, run the command

```pip install -e .```

This will also install all of the necessary dependencies.

## Running

At the moment the only files you can run are

```python ./etrombone/audio/core.py```

and

```python ./etrombone/inputs/vr/devices.py```

Which are the files for audio processing and OpenXR inputs respectively.

In future versions, the command to run will likely be something like

```python -m etrombone.live --output-device "MacBook Pro Speakers"```

import sounddevice as sd
import whisper
import numpy as np
from evdev import InputDevice, categorize, ecodes
import os
import subprocess

# Setup
os.environ['TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL'] = '1'
MOUSE_DEVICE = '/dev/input/event2'
BUTTON_CODE = 275  # BTN_SIDE
SAMPLE_RATE = 16000  # Whisper prefers 16kHz
CHANNELS = 1
STATUS_FILE= '/tmp/whisper-recording'

# Load Whisper model once
print("Loading Whisper model...")
model = whisper.load_model('large', download_root='/home/archduke/ai/models/whisper')
print("Ready! Press your thumb button to record.")

# Setup mouse device
device = InputDevice(MOUSE_DEVICE)

# Recording state
recording = False
audio_data = []

def audio_callback(indata, frames, time, status):
    """Called for each audio block while recording"""
    if status:
        print(status)
    audio_data.append(indata.copy())

# Main loop
stream = None
for event in device.read_loop():
    if event.type == ecodes.EV_KEY and event.code == BUTTON_CODE:
        if event.value == 1:  # Button pressed            
            #print("Recording...") not needed for service
            audio_data = []
            stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback)
            stream.start()
            open(STATUS_FILE, 'w').close()
            recording = True
            
        elif event.value == 0 and recording:  # Button released            
            #print("Processing...") not needed for service
            stream.stop()
            stream.close()
            os.remove(STATUS_FILE)
            recording = False
            
            # Convert audio data to format Whisper expects
            audio_array = np.concatenate(audio_data, axis=0).flatten()
            
            # Transcribe
            result = model.transcribe(audio_array,  fp16=False)
            subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/complete.oga'])
            text = result['text']            
            print(f"Text to copy: '{text}'")
            subprocess.run(['wl-copy'], input=text, text=True)
            subprocess.run(['wtype', '-M', 'ctrl', 'v', '-m', 'ctrl'])
            

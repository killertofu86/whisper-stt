import sounddevice as sd
import whisper
import numpy as np
from evdev import InputDevice, categorize, ecodes
import os
import subprocess
import configparser

# Read configuration
config = configparser.ConfigParser()
config_path = os.path.expanduser('~/.config/whisper-stt/config.ini')
config.read(config_path)

# Load settings with individual fallbacks
MODEL_SIZE = config.get('Model', 'size', fallback='large')
LANGUAGE = config.get('Model', 'language', fallback='auto')
MODEL_PATH = config.get('Model', 'model_path', fallback=os.path.expanduser('~/ai/models/whisper'))
SAMPLE_RATE = config.getint('Audio', 'sample_rate', fallback=16000)
CHANNELS = config.getint('Audio', 'channels', fallback=1)
AUDIO_DEVICE = config.get('Audio', 'audio_device', fallback='default')
BEEP_SOUND = config.get('Audio', 'beep_sound', fallback='/usr/share/sounds/freedesktop/stereo/complete.oga')
MOUSE_DEVICE = config.get('Input', 'mouse_device', fallback='/dev/input/event2')
BUTTON_CODE = config.getint('Input', 'button_code', fallback=275)
ROCM_EXPERIMENTAL = config.getboolean('System', 'rocm_experimental', fallback=True)
STATUS_FILE = config.get('System', 'status_file', fallback='/tmp/whisper-recording')

# Setup environment
if ROCM_EXPERIMENTAL:
    os.environ['TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL'] = '1'

# Load Whisper model once
print("Loading Whisper model...")
model = whisper.load_model(MODEL_SIZE, download_root=MODEL_PATH)
print(f"Ready! Model: {MODEL_SIZE}, Language: {LANGUAGE}")

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
            audio_data = []
            stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback, device=AUDIO_DEVICE)
            stream.start()
            open(STATUS_FILE, 'w').close()
            recording = True
            
        elif event.value == 0 and recording:  # Button released            
            stream.stop()
            stream.close()
            os.remove(STATUS_FILE)
            recording = False
            
            # Convert audio data to format Whisper expects
            audio_array = np.concatenate(audio_data, axis=0).flatten()
            
            # Transcribe with language setting
            language_param = None if LANGUAGE == 'auto' else LANGUAGE
            result = model.transcribe(audio_array, language=language_param, fp16=False)
            subprocess.run(['paplay', BEEP_SOUND])
            text = result['text']            
            print(f"Text to copy: '{text}'")
            subprocess.run(['wl-copy'], input=text, text=True)
            subprocess.run(['wtype', '-M', 'ctrl', 'v', '-m', 'ctrl'])
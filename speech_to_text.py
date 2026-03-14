import sounddevice as sd
import whisper
import numpy as np
from evdev import InputDevice, categorize, ecodes, UInput
import os
import subprocess
import configparser
from scipy import signal
import threading
import time

# Read configuration
config = configparser.ConfigParser()
config_path = os.path.expanduser('~/.config/whisper-stt/config.ini')
config.read(config_path)

MODEL_SIZE = config.get('Model', 'size', fallback='large')
LANGUAGE = config.get('Model', 'language', fallback='auto'); LANGUAGE = None if LANGUAGE == 'auto' else LANGUAGE
MODEL_PATH = config.get('Model', 'model_path', fallback=os.path.expanduser('~/ai/models/whisper'))
SAMPLE_RATE = config.getint('Audio', 'sample_rate', fallback=16000)
CHANNELS = config.getint('Audio', 'channels', fallback=1)
AUDIO_DEVICE = config.get('Audio', 'audio_device', fallback='default')
BEEP_SOUND = config.get('Audio', 'beep_sound', fallback='/usr/share/sounds/freedesktop/stereo/complete.oga')
MOUSE_DEVICE = config.get('Input', 'mouse_device', fallback='/dev/input/event2')
BUTTON_CODE = config.getint('Input', 'button_code', fallback=275)
ROCM_EXPERIMENTAL = config.getboolean('System', 'rocm_experimental', fallback=True)
STATUS_FILE = config.get('System', 'status_file', fallback='/tmp/whisper-recording')
MIN_DURATION = config.getfloat('Audio', 'min_duration', fallback=0.3)
MIN_AMPLITUDE = config.getfloat('Audio', 'min_amplitude', fallback=0.01)
GRAB_DEVICE = config.getboolean('Input', 'grab_device', fallback=True)
MODE = config.get('Input', 'mode', fallback='push_to_talk')
VAD_SILENCE_DURATION = config.getfloat('Input', 'vad_silence_duration', fallback=1.5)

VAD_MODE = (MODE == 'vad')
SESSION_TYPE = os.environ.get('XDG_SESSION_TYPE', 'wayland')

if ROCM_EXPERIMENTAL:
    os.environ['TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL'] = '1'

print('Loading Whisper model...')
model = whisper.load_model(MODEL_SIZE, download_root=MODEL_PATH)
print(f'Ready! Model: {MODEL_SIZE}, Language: {LANGUAGE}, Mode: {MODE}')

device = InputDevice(MOUSE_DEVICE)
if GRAB_DEVICE:
    ui = UInput.from_device(device)
    device.grab()

recording = False
audio_data = []
last_audio_time = 0.0
stream = None

def audio_callback(indata, frames, time_info, status):
    global last_audio_time
    if status:
        print(status)
    audio_data.append(indata.copy())
    if VAD_MODE:
        rms = np.sqrt(np.mean(indata**2))
        if rms > MIN_AMPLITUDE:
            last_audio_time = time.time()

def find_audio_device(name_pattern):
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if name_pattern.lower() in dev['name'].lower() and dev['max_input_channels'] > 0:
            return i
    return None

def stop_and_transcribe():
    global recording, stream
    stream.stop()
    stream.close()
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)
    recording = False
    audio_array = np.concatenate(audio_data, axis=0).flatten()
    threading.Thread(target=transcribe, args=(audio_array, LANGUAGE)).start()

def vad_monitor():
    start = time.time()
    while recording:
        time.sleep(0.1)
        since_last = time.time() - last_audio_time
        since_start = time.time() - start
        if since_start > VAD_SILENCE_DURATION and since_last >= VAD_SILENCE_DURATION:
            stop_and_transcribe()
            return

def transcribe(audio_array, language_param):
    audio_array = signal.resample(audio_array, int(len(audio_array) * 16000 / SAMPLE_RATE))
    result = model.transcribe(audio_array, language=language_param, fp16=False)
    subprocess.run(['paplay', '--volume=32768', BEEP_SOUND])
    text = result['text'].strip()
    if SESSION_TYPE == 'x11':
        subprocess.run(['xclip', '-selection', 'clipboard'], input=text, text=True)
        subprocess.run(['xdotool', 'key', 'ctrl+v'])
    else:
        subprocess.run(['wl-copy'], input=text, text=True)
        subprocess.run(['sh', '-c', 'echo "key ctrl+v" | dotool'])

subprocess.run(['paplay', '--volume=32768', BEEP_SOUND])

stream = None
for event in device.read_loop():
    if event.type == ecodes.EV_KEY and event.code == BUTTON_CODE:
        if event.value == 1:
            audio_data = []
            last_audio_time = time.time()
            stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback, device=find_audio_device(AUDIO_DEVICE))
            stream.start()
            open(STATUS_FILE, 'w').close()
            recording = True
            if VAD_MODE:
                threading.Thread(target=vad_monitor, daemon=True).start()
        elif event.value == 0 and recording:
            if not VAD_MODE:
                stop_and_transcribe()
    else:
        ui.write_event(event)
        ui.syn()

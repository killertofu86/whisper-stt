# Whisper Speech-to-Text for Linux (Wayland)

A system-wide speech-to-text solution for Linux using OpenAI's Whisper model with GPU acceleration.

## Features

- 🎤 **Push-to-talk** or **VAD mode** (voice activity detection - auto-stop on silence)
- 🚀 GPU-accelerated transcription (~0.95s latency with AMD ROCm)
- 🌍 Multi-language support (auto-detect, English, German, Japanese)
- 📊 Waybar integration with visual indicators
- ⚙️ Configurable model sizes (small/medium/large)
- 🔄 Automatic audio device detection
- 📋 Clipboard workflow with auto-paste
- 🎯 Silence detection to skip empty recordings
- 🖥️ Works on both Wayland and X11 (auto-detects)

## Modes

### Push-to-talk (default)
Hold button → speak → release → transcription starts.

### VAD mode (Voice Activity Detection)
Press button once → speak → auto-stops after configurable silence duration (default: 1.5s).
Press button again during recording to manually stop and transcribe immediately.
Great for longer dictation - no need to hold the button.

Set in config:
```ini
[Input]
mode = vad                          # or push_to_talk
vad_silence_duration = 1.5          # seconds of silence before auto-stop (after speech detected)
vad_initial_silence_duration = 5.0  # seconds to wait before auto-stop if no speech detected yet
```

### Display Server Support
- Wayland: uses wl-copy + dotool
- X11: uses xclip + xdotool
- Auto-detects via XDG_SESSION_TYPE environment variable

## Requirements

- Arch Linux (or similar)
- Wayland compositor (tested with niri)
- AMD GPU with ROCm support (or adapt for CUDA/CPU)
- Python 3.11+
- Waybar (optional, for UI integration)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/killertofu86/whisper-stt.git
cd whisper-stt
```

2. Create Python virtual environment:
```bash
python3.11 -m venv ~/coding/python/venv/whisper-stt
source ~/coding/python/venv/whisper-stt/bin/activate
```

3. Install dependencies:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/nightly/rocm7.0
pip install openai-whisper sounddevice scipy evdev
```

4. Install system dependencies:
```bash
# Wayland:
sudo pacman -S wl-clipboard rofi dotool
# X11:
sudo pacman -S xclip xdotool
```

5. Enable and start the dotool daemon:
```bash
systemctl --user enable --now dotool
```
If no systemd service exists, create `~/.config/systemd/user/dotool.service`:
```ini
[Unit]
Description=Dotool daemon for input simulation

[Service]
ExecStart=/usr/bin/dotoold
Restart=on-failure

[Install]
WantedBy=default.target
```

6. Create config directory and copy config file:
```bash
mkdir -p ~/.config/whisper-stt
cp config.ini ~/.config/whisper-stt/
```

7. Edit the config file to match your setup (audio device, mouse button, etc.)

8. Copy systemd service file:
```bash
cp systemd/whisper-stt.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now whisper-stt
```

9. (Optional) Install waybar scripts:
```bash
mkdir -p ~/scripts/whisper
cp scripts/* ~/scripts/whisper/
chmod +x ~/scripts/whisper/*.sh
```

## Configuration

Edit `~/.config/whisper-stt/config.ini` to customize:

```ini
[Model]
size = large                  # small / medium / large / large-v3-turbo
language = auto               # auto / en / de / ja

[Audio]
audio_device = CORSAIR        # partial name match of your mic
sample_rate = 48000
min_amplitude = 0.005         # VAD/silence threshold (tune to your environment)

[Input]
button_code = 275             # evdev code of your mouse button
mode = vad                          # push_to_talk / vad
vad_silence_duration = 1.5          # silence timeout after speech onset
vad_initial_silence_duration = 5.0  # silence timeout before first speech (longer grace period)
```

## Usage

### Push-to-talk
1. Press and hold your configured mouse button
2. Speak your text
3. Release → text is transcribed and pasted

### VAD mode
1. Click into a text field
2. Press button once
3. Speak (as long as you want)
4. Either pause for ~1.5s (auto-stop) or press button again (manual stop) → transcribe and paste

Use waybar buttons (if configured) to:
- Toggle service on/off
- Switch model sizes
- Change language modes

## Performance

With AMD 7900 XTX and ROCm 7.02:
- Small model: ~0.48s
- Medium model: ~0.77s
- Large model: ~0.95s

## Known Issues

- Chrome requires FFMSB extension to prevent back navigation
- Some applications may lose focus after recording

## License & Usage

This code is provided as-is for anyone to use, fork, or modify. Feel free to ask questions or submit issues, but please note:

**I am not actively developing features for others.** This is a personal project that I'm sharing with the community. You're welcome to fork and adapt it for your own needs.

## Development

This project was developed using [this Solveit notebook](https://share.solve.it.com/d/e1120924ec9fcd902adfdeeda97bdd16), which contains the full development process and discussions.

## Credits

Built with:
- [OpenAI Whisper](https://github.com/openai/whisper)
- AMD ROCm
- Various open-source Linux tools

---

*If you find this useful, feel free to star the repo or share it with others!*

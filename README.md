# Whisper Speech-to-Text for Linux (Wayland)

A system-wide push-to-talk speech-to-text solution for Linux using OpenAI's Whisper model with GPU acceleration.

## Features

- 🎤 Push-to-talk with configurable mouse button
- 🚀 GPU-accelerated transcription (~0.95s latency with AMD ROCm)
- 🌍 Multi-language support (auto-detect, English, German, Japanese)
- 📊 Waybar integration with visual indicators
- ⚙️ Configurable model sizes (small/medium/large)
- 🔄 Automatic audio device detection
- 📋 Clipboard workflow with auto-paste
- 🎯 Silence detection to skip empty recordings
```

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
sudo pacman -S wtype wl-clipboard rofi
```

5. Create config directory and copy config file:
```bash
mkdir -p ~/.config/whisper-stt
cp config.ini ~/.config/whisper-stt/
```

6. Edit the config file to match your setup (audio device, mouse button, etc.)

7. Copy systemd service file:
```bash
cp systemd/whisper-stt.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now whisper-stt
```

8. (Optional) Install waybar scripts:
```bash
mkdir -p ~/scripts/whisper
cp scripts/* ~/scripts/whisper/
chmod +x ~/scripts/whisper/*.sh
```

## Configuration

Edit `~/.config/whisper-stt/config.ini` to customize:

- Model size (small/medium/large)
- Language mode (auto/en/de/ja)
- Audio device pattern
- Mouse button code
- Sample rate and other audio settings
- Silence detection thresholds

## Usage

1. Press and hold your configured mouse button
2. Speak your text
3. Release the button
4. Text is automatically transcribed and pasted

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

## Credits

Built with:
- [OpenAI Whisper](https://github.com/openai/whisper)
- AMD ROCm
- Various open-source Linux tools
- Solve It (s)
---

## Development

This project was developed using [this Solveit notebook](https://share.solve.it.com/d/e1120924ec9fcd902adfdeeda97bdd16), which contains the full development process and discussions.


*If you find this useful, feel free to star the repo or share it with others!*
```

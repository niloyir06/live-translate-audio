# Live Audio Translation

A real-time audio translation application that captures system audio (loopback) and provides live transcription and translation from French to English.

## Features

- 🎧 **Real-time Audio Capture**: Captures system audio using loopback microphone
- 🗣️ **Live Transcription**: Uses Faster Whisper for speech-to-text conversion
- 🌐 **Instant Translation**: Translates French audio to English using Argos Translate
- ⚡ **Low Latency**: Processes audio in overlapping 5-second chunks with 3-second steps
- 🔄 **Continuous Processing**: Multi-threaded architecture for smooth real-time performance


## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/live-translate-audio.git
cd live-translate-audio
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage


1. Run the application:
```bash
python main.py
```

2. The application will:
   - Automatically download and install the French→English translation model
   - Load the Faster Whisper model for transcription
   - Start capturing and translating audio in real-time

3. Press `Ctrl+C` to stop the application

## Configuration

You can modify the following settings in `main.py`:

- `LANGUAGE`: Source language code (default: "fr" for French)
- `CHUNK_DURATION`: Audio processing window in seconds (default: 5)
- `STEP_DURATION`: How often to process new audio in seconds (default: 3)
- `SAMPLE_RATE`: Audio sample rate (default: 16000 Hz)

## How It Works

The application uses a multi-threaded architecture:

1. **Audio Reader Thread**: Continuously captures system audio using soundcard
2. **Transcriber Thread**: Processes audio chunks with Faster Whisper and translates with Argos
3. **Printer Thread**: Displays transcribed text and translations in real-time

## Dependencies

- `soundcard`: For audio capture
- `faster-whisper`: For speech-to-text transcription
- `argostranslate`: For translation
- `ctranslate2`: Backend for faster-whisper
- `numpy`: For audio processing

## Troubleshooting

### "No loopback microphone found"
- Ensure your system has loopback audio enabled
- On Windows, you might need to enable "Stereo Mix" in your audio settings
- Some systems require virtual audio cable software

### Poor transcription quality
- Ensure clear audio input
- Adjust `CHUNK_DURATION` for longer processing windows
- Consider using a larger Whisper model (change "base" to "small", "medium", etc.)

### Translation not working
- Check internet connection (required for initial model download)
- Verify that French→English language pack is installed

## License

This project is open source. Please check the license file for more details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

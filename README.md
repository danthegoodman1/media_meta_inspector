# Media Meta Inspector

A command-line tool for extracting audio metadata from remote audio files.

## Installation

```bash
pip install mutagen requests
```

## Usage

```bash
python main.py <audio_url>
```

## Example Output

```
Fetching metadata from: https://example.com/audio.mp3
Downloading the entire file (43.50 MB)...
Raw length value from file: 1425.32

Audio Metadata:
----------------------------------------
File Size: 43.50 MB
Duration: 23:45
Channels: Stereo
Sample Rate: 44100 Hz
Bitrate: 256 kbps
```

## Features

- Extracts audio metadata including duration, channels, sample rate, and bitrate
- Supports MP3, MP4, FLAC, OGG, and WAV formats
- Handles remote files via URL
- Downloads complete files for accurate duration information
- Provides fallbacks for various file types and edge cases

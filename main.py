#!/usr/bin/env python3
import sys
import requests
import tempfile
import os
from urllib.parse import urlparse
from pathlib import Path
import time
from mutagen._file import File
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE


def get_mp3_metadata(url):
    try:
        # Get the file size with a HEAD request
        head_response = requests.head(url, allow_redirects=True, timeout=10)
        total_size = int(head_response.headers.get("content-length", 0))

        print(f"Downloading the entire file ({total_size / (1024 * 1024):.2f} MB)...")
        response = requests.get(
            url, stream=True, timeout=60
        )  # Increased timeout for larger files

        # Get the file extension from the URL
        parsed_url = urlparse(url)
        file_extension = Path(parsed_url.path).suffix.lower()

        # Create a temp file for the file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            temp_path = temp_file.name

        try:
            # Try to parse the metadata based on file extension
            audio = None
            if file_extension == ".mp3":
                audio = MP3(temp_path)
            elif file_extension in [".m4a", ".mp4"]:
                audio = MP4(temp_path)
            elif file_extension == ".flac":
                audio = FLAC(temp_path)
            elif file_extension == ".ogg":
                audio = OggVorbis(temp_path)
            elif file_extension == ".wav":
                audio = WAVE(temp_path)
            else:
                audio = File(temp_path)

            if audio is not None and hasattr(audio, "info") and audio.info is not None:
                # Extract common audio properties
                info = audio.info

                # Print the actual length for debugging
                if hasattr(info, "length"):
                    print(f"Raw length value from file: {info.length}")

                # Get duration in minutes:seconds format
                if hasattr(info, "length"):
                    minutes, seconds = divmod(info.length, 60)
                    duration = f"{int(minutes)}:{int(seconds):02d}"
                else:
                    duration = "Unknown"

                # Get channel info (mono/stereo)
                channels = getattr(info, "channels", "Unknown")
                channel_text = (
                    "Mono"
                    if channels == 1
                    else "Stereo"
                    if channels == 2
                    else f"{channels} channels"
                )

                # Get sample rate
                sample_rate = getattr(info, "sample_rate", "Unknown")

                # Get bitrate
                bitrate = (
                    getattr(info, "bitrate", 0) // 1000
                    if hasattr(info, "bitrate")
                    else 0
                )  # Convert to kbps

                return {
                    "file_size": f"{total_size / (1024 * 1024):.2f} MB",
                    "duration": duration,
                    "channels": channel_text,
                    "sample_rate": f"{sample_rate} Hz"
                    if sample_rate != "Unknown"
                    else "Unknown",
                    "bitrate": f"{bitrate} kbps" if bitrate else "Unknown",
                }
            else:
                # If we couldn't get metadata with the standard approach,
                # try one more time with a generic File approach
                audio = File(temp_path)
                if (
                    audio is not None
                    and hasattr(audio, "info")
                    and audio.info is not None
                ):
                    info = audio.info
                    if hasattr(info, "length"):
                        print(f"Raw length value from fallback: {info.length}")
                        minutes, seconds = divmod(info.length, 60)
                        duration = f"{int(minutes)}:{int(seconds):02d}"
                    else:
                        duration = "Unknown"

                    channels = getattr(info, "channels", "Unknown")
                    channel_text = (
                        "Mono"
                        if channels == 1
                        else "Stereo"
                        if channels == 2
                        else f"{channels} channels"
                    )
                    sample_rate = getattr(info, "sample_rate", "Unknown")
                    bitrate = (
                        getattr(info, "bitrate", 0) // 1000
                        if hasattr(info, "bitrate")
                        else 0
                    )

                    return {
                        "file_size": f"{total_size / (1024 * 1024):.2f} MB",
                        "duration": duration,
                        "channels": channel_text,
                        "sample_rate": f"{sample_rate} Hz"
                        if sample_rate != "Unknown"
                        else "Unknown",
                        "bitrate": f"{bitrate} kbps" if bitrate else "Unknown",
                    }
                else:
                    return {
                        "error": "Could not extract metadata. The file may have non-standard formatting or may not be a valid audio file."
                    }
        except HeaderNotFoundError:
            print("MP3 headers not found in the file.")
            return {
                "file_size": f"{total_size / (1024 * 1024):.2f} MB",
                "duration": "Unknown (headers not found)",
                "channels": "Unknown",
                "sample_rate": "Unknown",
                "bitrate": "Unknown",
            }
        except Exception as e:
            print(f"Error extracting metadata: {str(e)}")
            return {"error": f"Error extracting metadata: {str(e)}"}
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        return {"error": f"Error retrieving metadata: {str(e)}"}


def main():
    if len(sys.argv) != 2:
        print("Usage: python mp3_metadata.py <audio_url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Fetching metadata from: {url}")
    start_time = time.time()

    metadata = get_mp3_metadata(url)

    elapsed_time = time.time() - start_time
    print(f"Process completed in {elapsed_time:.2f} seconds")

    if "error" in metadata:
        print("\nError:")
        print("-" * 40)
        print(metadata["error"])
    else:
        print("\nAudio Metadata:")
        print("-" * 40)
        for key, value in metadata.items():
            print(f"{key.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    main()

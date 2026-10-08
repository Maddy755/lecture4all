import os
import json
import whisper_timestamped

"""
Author: w4a-backend / modified for automatic multilingual transcription

Description:
    Automatically discovers all supported media files in the videos directory,
    lets Whisper detect the language, transcribes each file once, and saves
    timestamped JSON transcripts.

    No language is hardcoded.
    No filenames are hardcoded.
    Existing transcripts are not overwritten.
"""

VIDEOS_DIRECTORY = "./videos"
OUTPUT_DIRECTORY = "./transcriptions"

SUPPORTED_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mkv",
    ".avi",
    ".mov",
    ".mp3",
    ".wav",
    ".m4a",
}


def load_model(model_size="medium"):
    print(f"Loading Whisper model: {model_size}")

    model = whisper_timestamped.load_model(
        model_size,
        device="cuda"
    )

    return model


def transcribe_video(model, video_path):
    """
    Whisper automatically detects the language.

    No language is supplied here.
    """

    result = whisper_timestamped.transcribe(
        model,
        video_path
    )

    return result


def save_transcription(result, output_path):

    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=4,
            ensure_ascii=False
        )


def get_video_files():

    if not os.path.exists(VIDEOS_DIRECTORY):
        print(f"Videos directory does not exist: {VIDEOS_DIRECTORY}")
        return []

    files = []

    for filename in os.listdir(VIDEOS_DIRECTORY):

        extension = os.path.splitext(filename)[1].lower()

        if extension in SUPPORTED_EXTENSIONS:
            files.append(filename)

    files.sort()

    return files


def main():

    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    video_files = get_video_files()

    if not video_files:
        print("No supported media files found.")
        return

    print()
    print("=" * 70)
    print(f"Found {len(video_files)} media files")
    print("=" * 70)

    for filename in video_files:

        video_path = os.path.join(
            VIDEOS_DIRECTORY,
            filename
        )

        filename_without_extension = os.path.splitext(
            filename
        )[0]

        output_filename = (
            f"{filename_without_extension}_transcript.json"
        )

        output_path = os.path.join(
            OUTPUT_DIRECTORY,
            output_filename
        )

        # Never overwrite an existing transcript
        if os.path.exists(output_path):

            print()
            print(f"Skipping: {filename}")
            print("Transcript already exists.")

            continue

        print()
        print("=" * 70)
        print(f"Processing: {filename}")
        print("=" * 70)

        try:

            result = transcribe_video(
                model,
                video_path
            )

            detected_language = result.get(
                "language",
                "unknown"
            )

            print(
                f"Detected language: {detected_language}"
            )

            save_transcription(
                result,
                output_path
            )

            print(
                f"Saved: {output_filename}"
            )

        except Exception as e:

            print()
            print(f"ERROR processing: {filename}")
            print(f"Error: {e}")
            print("Continuing with next file...")

    print()
    print("=" * 70)
    print("Transcription process complete.")
    print("=" * 70)


if __name__ == "__main__":

    model = load_model()

    main()
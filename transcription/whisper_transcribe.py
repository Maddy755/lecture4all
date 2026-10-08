import os
import sys
import json
import whisper_timestamped

"""
Lecture4All batch video transcription

Processes all supported video files in ./videos
and saves Whisper timestamped JSON files in ./transcriptions.
"""

VIDEO_EXTENSIONS = (".mp4", ".webm", ".mkv", ".avi", ".mov")


def loadModel(model_size="medium"):
    """
    Use CUDA when available, otherwise CPU.
    """
    try:
        model = whisper_timestamped.load_model(model_size, device="cuda")
        print("Whisper model loaded using CUDA.")
        return model
    except Exception as e:
        print("CUDA unavailable. Falling back to CPU.")
        print(f"CUDA error: {e}")

        model = whisper_timestamped.load_model(model_size, device="cpu")
        print("Whisper model loaded using CPU.")
        return model


def transcribeVideo(model, videoPath):
    print(f"Transcribing: {videoPath}")
    result = whisper_timestamped.transcribe(model, videoPath)
    return result


def saveTranscription(result, output_json):
    os.makedirs("transcriptions", exist_ok=True)

    output_path = os.path.join("transcriptions", output_json)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"Saved: {output_path}")


if __name__ == "__main__":

    videos_directory = "./videos"
    output_directory = "./transcriptions"

    # Check videos directory
    if not os.path.exists(videos_directory):
        print(f"Video directory does not exist: {videos_directory}")
        sys.exit(1)

    # Find all supported videos
    video_files = [
        f for f in os.listdir(videos_directory)
        if f.lower().endswith(VIDEO_EXTENSIONS)
    ]

    video_files.sort()

    print(f"Found {len(video_files)} video files.")

    if len(video_files) == 0:
        print("No supported videos found.")
        sys.exit(0)

    print("\nVideos to process:")
    for video in video_files:
        print(f"  - {video}")

    print("\nLoading Whisper model...")
    model = loadModel("medium")

    os.makedirs(output_directory, exist_ok=True)

    for filename in video_files:

        video_path = os.path.join(videos_directory, filename)

        # Preserve the video filename as the transcript name
        video_name = os.path.splitext(filename)[0]
        output_json = f"{video_name}_transcript.json"
        output_path = os.path.join(output_directory, output_json)

        # Don't retranscribe existing files
        if os.path.exists(output_path):
            print(
                f"\nSkipping {filename} "
                f"(transcription already exists)."
            )
            continue

        print("\n" + "=" * 60)
        print(f"Processing: {filename}")
        print("=" * 60)

        try:
            result = transcribeVideo(model, video_path)

            saveTranscription(
                result,
                output_json
            )

            print(f"Completed: {filename}")

        except Exception as e:
            print(f"ERROR processing {filename}: {e}")
            print("Continuing with next video...")

    print("\nAll videos processed.")
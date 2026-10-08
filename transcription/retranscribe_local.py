import os
import json
import whisper_timestamped

VIDEOS_DIR = "./videos"
OUTPUT_DIR = "./transcriptions"

VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mkv",
    ".avi",
    ".mov",
    ".mp3",
    ".wav",
    ".m4a",
}

def load_model():
    print("Loading Whisper model...")
    return whisper_timestamped.load_model(
        "medium",
        device="cuda"
    )


def detect_language(model, video_path):
    """
    Detect the spoken language without hardcoding it.
    """

    print(f"Detecting language: {os.path.basename(video_path)}")

    result = whisper_timestamped.transcribe(
        model,
        video_path,
        language=None,
        vad=True
    )

    language = result.get("language")

    return language, result


def transcribe_video(model, video_path, language):
    """
    Transcribe using the language detected by Whisper.
    """

    print(
        f"Transcribing {os.path.basename(video_path)} "
        f"(detected language: {language})"
    )

    return whisper_timestamped.transcribe(
        model,
        video_path,
        language=language,
        vad=True
    )


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    model = load_model()

    # Automatically discover videos
    videos = [
        f for f in os.listdir(VIDEOS_DIR)
        if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS
    ]

    videos.sort()

    print(f"\nFound {len(videos)} media files.\n")

    for filename in videos:

        video_path = os.path.join(VIDEOS_DIR, filename)

        name = os.path.splitext(filename)[0]

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{name}_transcript_v2.json"
        )

        # Don't overwrite existing work
        if os.path.exists(output_path):
            print(f"Skipping existing: {filename}")
            continue

        print("\n" + "=" * 70)
        print(f"FILE: {filename}")
        print("=" * 70)

        try:

            # -------------------------------------------------
            # STEP 1: Detect language
            # -------------------------------------------------

            language, first_result = detect_language(
                model,
                video_path
            )

            print(f"Detected language: {language}")

            if not language:
                print("Could not determine language. Skipping.")
                continue

            # -------------------------------------------------
            # STEP 2: Transcribe using detected language
            # -------------------------------------------------

            result = transcribe_video(
                model,
                video_path,
                language
            )

            # -------------------------------------------------
            # STEP 3: Save
            # -------------------------------------------------

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

            print(f"Saved: {output_path}")

        except Exception as e:

            print(f"ERROR processing {filename}")
            print(e)

    print("\nAll videos processed.")


if __name__ == "__main__":
    main()
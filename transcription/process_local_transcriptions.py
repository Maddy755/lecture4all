import json
import os
import re

TRANSCRIPTION_DIRECTORY = "./transcriptions"
OUTPUT_DIRECTORY = "./processed_transcripts"

os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


def make_title(video_id):
    """
    Convert filenames such as:
    tamil_cse_aiml
    -> Tamil Cse Aiml
    """
    return video_id.replace("_", " ").title()


def process_transcript(filename):

    input_path = os.path.join(
        TRANSCRIPTION_DIRECTORY,
        filename
    )

    video_id = filename.replace("_transcript.json", "")

    output_filename = f"{video_id}_transcript.json"
    output_path = os.path.join(
        OUTPUT_DIRECTORY,
        output_filename
    )

    # Don't overwrite existing processed transcripts
    if os.path.exists(output_path):
        print(f"Skipping existing file: {output_filename}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        transcription = json.load(f)

    detected_language = transcription.get(
        "language",
        "unknown"
    )

    processed_transcript = {
        "id": video_id,
        "title": make_title(video_id),
        "speaker": "Unknown",
        "category": "Local Video",
        "date": "",
        "url": "",
        "m3u8": "",
        "thumbnail": "",
        "language": detected_language,
        "chunks": []
    }

    current_chunk = []
    chunk_start_time = None
    chunk_length = 12.0
    current_duration = 0.0

    for segment in transcription.get("segments", []):

        for word in segment.get("words", []):

            word_start = word.get("start")
            word_end = word.get("end")
            word_text = word.get("text", "").strip()

            if word_start is None or word_end is None:
                continue

            if not word_text:
                continue

            if chunk_start_time is None:
                chunk_start_time = word_start

            current_chunk.append(word_text)

            current_duration = word_end - chunk_start_time

            if current_duration >= chunk_length:

                processed_transcript["chunks"].append({
                    "text": " ".join(current_chunk),
                    "start": chunk_start_time,
                    "end": word_end
                })

                current_chunk = []
                chunk_start_time = None
                current_duration = 0.0

    # Save remaining words
    if current_chunk and chunk_start_time is not None:

        processed_transcript["chunks"].append({
            "text": " ".join(current_chunk),
            "start": chunk_start_time,
            "end": transcription.get("segments", [{}])[-1].get(
                "end",
                chunk_start_time
            )
        })

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            processed_transcript,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(
        f"Processed: {filename} "
        f"-> {output_filename} "
        f"({len(processed_transcript['chunks'])} chunks)"
    )


if __name__ == "__main__":

    files = [
        f
        for f in os.listdir(TRANSCRIPTION_DIRECTORY)
        if f.endswith("_transcript.json")
    ]

    # Only process the NEW local videos
    local_ids = {
        "11058",
        "hindi_cse_operations",
        "hindi_cse_software_eng",
        "hindi_dbms_short",
        "malayalam_cs_short1",
        "tamil_cse_aiml",
        "tamil_oops_intro"
    }

    files = [
        f
        for f in files
        if f.replace("_transcript.json", "") in local_ids
    ]

    print(f"Found {len(files)} local transcripts.")

    for filename in sorted(files):
        process_transcript(filename)

    print("\nProcessing complete.")
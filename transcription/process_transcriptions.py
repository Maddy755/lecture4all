import json
import os

"""
Automatically processes Whisper transcripts into the format expected
by the Lecture4All ChromaDB ingestion pipeline.

Works with:
    11058_transcript.json
    hindi_cse_operations_transcript.json
    tamil_cse_aiml_transcript.json
    etc.

No filenames or languages are hardcoded.
"""


TRANSCRIPTION_DIRECTORY = "./transcriptions"
OUTPUT_DIRECTORY = "./processed_transcripts"

CHUNK_LENGTH = 12.0


def make_title(filename):

    name = os.path.splitext(filename)[0]

    # Remove the transcript suffix
    if name.endswith("_transcript"):
        name = name[:-11]

    # Convert underscores to spaces
    title = name.replace("_", " ")

    return title.strip()


def process_transcript(filename):

    input_path = os.path.join(
        TRANSCRIPTION_DIRECTORY,
        filename
    )

    output_filename = filename

    output_path = os.path.join(
        OUTPUT_DIRECTORY,
        output_filename
    )

    if os.path.exists(output_path):

        print(
            f"Skipping existing processed file: {filename}"
        )

        return False

    try:

        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as f:

            transcription = json.load(f)

    except Exception as e:

        print(
            f"Could not read {filename}: {e}"
        )

        return False

    # ---------------------------------------------------------
    # Basic metadata
    # ---------------------------------------------------------

    base_name = os.path.splitext(filename)[0]

    if base_name.endswith("_transcript"):
        video_id = base_name[:-11]
    else:
        video_id = base_name

    title = make_title(filename)

    speaker = "Unknown"

    category = "Local Video"

    date = ""

    url = ""

    m3u8 = ""

    thumbnail = ""

    detected_language = transcription.get(
        "language",
        "unknown"
    )

    # ---------------------------------------------------------
    # Build processed transcript
    # ---------------------------------------------------------

    processed_transcript = {

        "id": video_id,

        "title": title,

        "speaker": speaker,

        "category": category,

        "date": date,

        "url": url,

        "m3u8": m3u8,

        "thumbnail": thumbnail,

        "language": detected_language,

        "chunks": []
    }

    # ---------------------------------------------------------
    # Create approximately 12-second chunks
    # ---------------------------------------------------------

    current_chunk = []

    chunk_start_time = None

    last_word_end = None

    current_duration = 0.0

    segments = transcription.get(
        "segments",
        []
    )

    for segment in segments:

        words = segment.get(
            "words",
            []
        )

        # Some Whisper output may not contain
        # word-level timestamps.
        if not words:

            text = segment.get(
                "text",
                ""
            ).strip()

            if text:

                processed_transcript["chunks"].append({

                    "text": text,

                    "start": segment.get(
                        "start",
                        0.0
                    ),

                    "end": segment.get(
                        "end",
                        0.0
                    )
                })

            continue

        for word in words:

            word_start = word.get(
                "start"
            )

            word_end = word.get(
                "end"
            )

            word_text = word.get(
                "text",
                ""
            ).strip()

            if word_start is None or word_end is None:
                continue

            if not word_text:
                continue

            # Start a new chunk
            if chunk_start_time is None:

                chunk_start_time = word_start

                current_duration = 0.0

            word_duration = max(
                0.0,
                word_end - word_start
            )

            current_chunk.append(
                word_text
            )

            current_duration += word_duration

            last_word_end = word_end

            # Finish approximately 12-second chunk
            if current_duration >= CHUNK_LENGTH:

                processed_transcript["chunks"].append({

                    "text": " ".join(
                        current_chunk
                    ),

                    "start": chunk_start_time,

                    "end": last_word_end
                })

                current_chunk = []

                chunk_start_time = None

                current_duration = 0.0

    # ---------------------------------------------------------
    # Save remaining words
    # ---------------------------------------------------------

    if current_chunk:

        processed_transcript["chunks"].append({

            "text": " ".join(
                current_chunk
            ),

            "start": chunk_start_time,

            "end": last_word_end
        })

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            processed_transcript,
            f,
            indent=4,
            ensure_ascii=False
        )

    print()
    print(f"Processed: {filename}")
    print(f"Language : {detected_language}")
    print(
        f"Chunks   : "
        f"{len(processed_transcript['chunks'])}"
    )
    print(
        f"Saved    : {output_path}"
    )

    return True


def main():

    os.makedirs(
        OUTPUT_DIRECTORY,
        exist_ok=True
    )

    if not os.path.exists(
        TRANSCRIPTION_DIRECTORY
    ):

        print(
            "Transcription directory does not exist."
        )

        return

    transcript_files = [

        filename

        for filename in os.listdir(
            TRANSCRIPTION_DIRECTORY
        )

        if filename.endswith(
            "_transcript.json"
        )
    ]

    transcript_files.sort()

    print(
        f"Found {len(transcript_files)} "
        f"transcript files."
    )

    processed_count = 0

    for filename in transcript_files:

        if process_transcript(filename):
            processed_count += 1

    print()
    print("=" * 70)
    print(
        f"Processed {processed_count} new transcripts."
    )
    print("=" * 70)


if __name__ == "__main__":

    main()
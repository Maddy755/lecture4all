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


def clean_repeated_chars(text):
    if not text:
        return ""
    import re
    return re.sub(r'(.)\1{3,}', r'\1', text)


def remove_repetitive_ngrams_from_words(words, max_n=5, max_repeats=1):
    result = list(words)
    changed = True
    while changed:
        changed = False
        for n in range(max_n, 0, -1):
            i = 0
            new_result = []
            while i < len(result):
                ngram = [clean_repeated_chars(w.get('text', '').strip()) for w in result[i:i+n]]
                if len(ngram) < n or not any(ngram):
                    new_result.extend(result[i:])
                    break
                repeat_count = 1
                j = i + n
                while j + n <= len(result) and [clean_repeated_chars(w.get('text', '').strip()) for w in result[j:j+n]] == ngram:
                    repeat_count += 1
                    j += n
                if repeat_count > max_repeats:
                    for _ in range(max_repeats):
                        new_result.extend(result[i:i+n])
                    i = j
                    changed = True
                else:
                    new_result.extend(result[i:i+n])
                    i += n
            result = new_result
    return result


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
    # Basic metadata defaults
    # ---------------------------------------------------------

    base_name = os.path.splitext(filename)[0]

    if base_name.endswith("_transcript"):
        video_id = base_name[:-11]
    else:
        video_id = base_name

    title = make_title(filename)
    speaker = "Unknown"
    category = "General"
    date = "Unknown"
    url = f"https://lecture2go.uni-hamburg.de/l2go/-/get/v/{video_id}"
    m3u8 = f"https://lecture2go.uni-hamburg.de/vod/_definst_/mp4:{video_id}.mp4/playlist.m3u8"
    thumbnail = f"https://lecture2go.uni-hamburg.de/vod/_definst_/mp4:{video_id}.mp4/preview.jpg"

    meta_path = os.path.join("metadata", f"{video_id}_metadata.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as mf:
                m_list = json.load(mf)
                m_data = m_list[0] if isinstance(m_list, list) and m_list else m_list
                title = m_data.get("title", title)
                speaker = m_data.get("speaker", speaker)
                category = m_data.get("category", category)
                date = m_data.get("date", date)
                url = m_data.get("url", url)
                m3u8 = m_data.get("m3u8", m3u8)
                thumbnail = m_data.get("thumbnail", thumbnail)
        except Exception as me:
            print(f"Notice: could not load metadata from {meta_path}: {me}")

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
        if words:
            words = remove_repetitive_ngrams_from_words(words, max_n=5, max_repeats=1)

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
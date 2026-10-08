import json
import os
import sys

"""
Author: w4a-backend
Description: This script processes the transcriptions and metadata to create processed transcripts.
"""

transcription_directory = "transcriptions"
output_directory = "./processed_transcripts"
os.makedirs(output_directory, exist_ok=True)

def process_transcript(id):
    metadata_filename = f"{id}_metadata.json"
    metadata_path = os.path.join("metadata", metadata_filename)
    filename = f"{id}_transcript.json"
    if not os.path.exists(os.path.join(transcription_directory, filename)) or not os.path.exists(metadata_path):
        print(f"Transcription or metadata file does not exist for {id}. Skipping...")
        return
    output_filename = os.path.join(output_directory, filename)
    if os.path.exists(output_filename):
        print(f"Skipping file as it already exists: {filename}")
        return
    id = filename.split("_")[0]
    with open(metadata_path, "r") as metadata_file:
        metadata = json.load(metadata_file)
        speaker = title = category = date = url = m3u8 = thumbnail = None
        entry = metadata[0]
        speaker = entry["speaker"]
        title = entry["title"]
        m3u8 = entry["m3u8"]
        thumbnail = entry["thumbnail"]
        url = entry["url"]
        category = entry["category"]
        date = entry["date"]
    with open(os.path.join(transcription_directory, filename), "r", encoding="utf-8") as f:
        transcription = json.load(f)
        detected_language = transcription.get("language", "en")

    processed_transcript = {
        "id": id,
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
    
    current_chunk = []
    current_time = 0.0
        chunk_length = 12.0
        chunk_start_time = 0.0
        
        for segment in transcription.get("segments", []):
            for word in segment.get("words", []):
                word_start = word['start']
                word_end = word['end']
                word_text = word['text']
                word_duration = word_end - word_start

                if not current_chunk:
                    chunk_start_time = word_start
                
                current_chunk.append(word_text)
                current_time += word_duration
                
                # Check if the current chunk is over the target length
                if current_time >= chunk_length:
                    processed_transcript["chunks"].append({
                        "text": " ".join(current_chunk),
                        "start": chunk_start_time,
                        "end": word_end
                    })
                    current_chunk = []
                    current_time = 0.0
        if current_chunk:
            processed_transcript["chunks"].append({
                "text": " ".join(current_chunk),
                "start": chunk_start_time,
                "end": segment['end']
            })
    with open(output_filename, "w") as output_file:
        json.dump(processed_transcript, output_file, ensure_ascii=False, indent=4)
    print(f"Processed file saved: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_transcriptions.py <start_index> <end_index>")
    start_index = int(sys.argv[1])
    end_index = int(sys.argv[2])
    print(f"Processing transcriptions from {start_index} to {end_index}")
    for i in range(start_index, end_index + 1):
        print(f"Processing transcript {i}")
        process_transcript(i)

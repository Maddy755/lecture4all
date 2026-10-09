import chromadb
import json
import os

client = chromadb.HttpClient(
    host="chromadb",
    port=8000
)

collection = client.get_collection(
    name="w4a-v2"
)

transcript_dir = "/processed_transcripts"

video_ids = [
    "37694",
    "70050",
    "70605",
    "70865",
]

for video_id in video_ids:

    transcript_path = os.path.join(
        transcript_dir,
        f"{video_id}_transcript.json"
    )

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    original_m3u8 = transcript["m3u8"]

    print(f"\nRestoring {video_id}")
    print(original_m3u8)

    records = collection.get(
        where={"video_id": video_id},
        include=["metadatas"]
    )

    for record_id, metadata in zip(
        records["ids"],
        records["metadatas"]
    ):

        new_metadata = dict(metadata)
        new_metadata["m3u8_url"] = original_m3u8

        collection.update(
            ids=[record_id],
            metadatas=[new_metadata]
        )

    print(
        f"Restored {len(records['ids'])} records for {video_id}"
    )

print("\nDone.")
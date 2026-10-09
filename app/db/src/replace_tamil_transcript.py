import chromadb
import json
import embedding_function as ef

client = chromadb.HttpClient(
    host="chromadb",
    port=8000
)

use_ef = ef.get_embedding_function()

collection = client.get_collection(
    name="w4a-v2",
    embedding_function=use_ef
)

video_id = "tamil_cse_aiml"

# Find existing records
existing = collection.get(
    where={"video_id": video_id}
)

print(f"Existing records: {len(existing['ids'])}")

# Delete only this video's records
if existing["ids"]:
    collection.delete(ids=existing["ids"])
    print("Old Tamil transcript deleted.")

# Load corrected transcript
with open(
    "/processed_transcripts/tamil_cse_aiml_transcript_fixed.json",
    "r",
    encoding="utf-8"
) as f:
    transcript = json.load(f)

base_metadata = {
    "video_id": transcript["id"],
    "title": transcript["title"],
    "speaker": transcript["speaker"],
    "date": transcript["date"],
    "category": transcript["category"],
    "thumbnail_url": transcript["thumbnail"],
    "m3u8_url": transcript["m3u8"],
}

ids = []
documents = []
metadatas = []

for i, chunk in enumerate(transcript["chunks"]):

    documents.append(chunk["text"])

    metadatas.append({
        **base_metadata,
        "start": chunk["start"],
        "end": chunk["end"],
    })

    ids.append(f"{video_id}0{i}")

# Add corrected transcript
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids,
)

print(f"Added {len(ids)} corrected chunks.")
print("Language:", transcript.get("language"))
print("Done.")
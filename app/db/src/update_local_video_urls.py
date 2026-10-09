import chromadb
import os

# Connect to Chroma
client = chromadb.HttpClient(
    host="chromadb",
    port=8000
)

collection_name = "w4a-v2"

collection = client.get_collection(
    name=collection_name
)

# Local videos mounted inside the db container
video_dir = "/processed_transcripts/../videos"

# Better: use the actual mounted video directory
video_dir = "/transcription/videos"

# Build:
# video basename -> actual filename
#
# Example:
# hindi_cse_operations -> hindi_cse_operations.webm
video_files = {}

for filename in os.listdir(video_dir):

    full_path = os.path.join(video_dir, filename)

    if not os.path.isfile(full_path):
        continue

    name, extension = os.path.splitext(filename)

    if extension.lower() in [".mp4", ".webm", ".mkv"]:

        video_files[name] = filename


print("Local videos found:")
for name, filename in sorted(video_files.items()):
    print(f"  {name} -> {filename}")


# Get all records currently in the collection
data = collection.get(
    include=["metadatas"]
)

ids = data["ids"]
metadatas = data["metadatas"]

updated_ids = []

for record_id, metadata in zip(ids, metadatas):

    video_id = metadata.get("video_id")

    if not video_id:
        continue

    # Only update records for which we have a local video
    if video_id not in video_files:
        continue

    filename = video_files[video_id]

    local_url = f"/video-file/{filename}"

    # Keep all existing metadata
    new_metadata = dict(metadata)

    # Replace only the video URL
    new_metadata["m3u8_url"] = local_url

    collection.update(
        ids=[record_id],
        metadatas=[new_metadata]
    )

    updated_ids.append(record_id)

    print(
        f"Updated {record_id}: "
        f"{video_id} -> {local_url}"
    )


print()
print(f"Updated {len(updated_ids)} Chroma records.")
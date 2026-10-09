import chromadb
from chromadb.utils import embedding_functions
import json
import os
import embedding_function as ef

host = str(input(
    "Enter the host, if you are in the docker container db-env enter \"chomadb\", else enter \"localhost\": "))
client = chromadb.HttpClient(host=host , port=8000)

use_ef = ef.get_embedding_function()

collection_name = input("Enter the collection name: ")
if not collection_name in client.list_collections():
    client.create_collection(collection_name)
collection = client.get_collection(name=collection_name, embedding_function=use_ef)

def add_transcript(transcript_json):
    video_id = transcript_json["id"]
    title = transcript_json["title"]
    speaker = transcript_json["speaker"]
    date = transcript_json["date"]
    m3u8_url = transcript_json["m3u8"]
    category = transcript_json["category"]
    thumbnail_url = transcript_json["thumbnail"]
    base_metadata = {
        "video_id": video_id, 
        "title": title,
        "speaker": speaker,
        "date": date,
        "category": category,
        "thumbnail_url": thumbnail_url,
        "m3u8_url": m3u8_url
        }

    id = 0
    for chunk in transcript_json.get("chunks", []):
        text = chunk.get("text")
        start = chunk.get("start")
        end = chunk.get("end")
        metadata = {**base_metadata, "start": start, "end": end}
        vid = f"{video_id}0{id}"
        collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[vid],
        )
        id += 1

def transcript_exists(video_id):
    """
    Check if a transcript with given video_id exists in the collection
    Args:
        video_id: The video ID to check
    Returns:
        bool: True if transcript exists, False otherwise
    """
    existing_docs = collection.get(
        where={"video_id": video_id}
    )
    return len(existing_docs['ids']) > 0

path = str(input("Enter the path to the directory containing the transcripts: "))
n = 1
for file in os.listdir(path):
    filepath = os.path.join(path, file)
    with open(filepath, "r") as input_file:
        json_input = json.load(input_file)
        if transcript_exists(json_input["id"]):
            print(f"Transcript {json_input['id']} already exists in the collection.")
        else:
            print(f"Adding transcript {json_input['id']} ...")
            add_transcript(json_input)
            print(f"Transcript {json_input['id']} added successfully. {n} transcripts added.")
            n += 1
print(f"Added {n-1} transcripts to the collection {collection_name}.")





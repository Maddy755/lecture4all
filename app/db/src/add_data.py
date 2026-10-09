import chromadb
from chromadb.utils import embedding_functions
import json
import os
import sys

try:
    import embedding_function as ef
except ImportError:
    from src import embedding_function as ef

def get_args():
    # Allow arguments via CLI, environment variables, or interactive input
    host = os.environ.get("CHROMA_HOST")
    if not host and len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        host = sys.argv[1]
    if not host:
        if sys.stdin.isatty():
            host = input('Enter the host ("chromadb" or "localhost"): ').strip()
        else:
            host = "chromadb" if os.path.exists("/.dockerenv") else "localhost"

    collection_name = os.environ.get("COLLECTION_NAME")
    if not collection_name and len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
        collection_name = sys.argv[2]
    if not collection_name:
        if sys.stdin.isatty():
            collection_name = input("Enter the collection name [w4a-v2]: ").strip() or "w4a-v2"
        else:
            collection_name = "w4a-v2"

    path = os.environ.get("TRANSCRIPTS_PATH")
    if not path and len(sys.argv) > 3 and not sys.argv[3].startswith("-"):
        path = sys.argv[3]
    if not path:
        default_path = "/processed_transcripts" if os.path.exists("/processed_transcripts") else "transcription/processed_transcripts"
        if sys.stdin.isatty():
            path = input(f"Enter path to transcripts directory [{default_path}]: ").strip() or default_path
        else:
            path = default_path

    overwrite = "--overwrite" in sys.argv or os.environ.get("OVERWRITE", "1") == "1"
    return host, collection_name, path, overwrite

def add_transcript(transcript_json, collection, overwrite=True):
    video_id = transcript_json["id"]
    title = transcript_json.get("title", "")
    speaker = transcript_json.get("speaker", "")
    date = transcript_json.get("date", "")
    m3u8_url = transcript_json.get("m3u8", "")
    category = transcript_json.get("category", "")
    thumbnail_url = transcript_json.get("thumbnail", "")
    language = transcript_json.get("language", "en")
    
    base_metadata = {
        "video_id": video_id, 
        "title": title,
        "speaker": speaker,
        "date": date,
        "category": category,
        "thumbnail_url": thumbnail_url,
        "m3u8_url": m3u8_url,
        "language": language
    }

    chunks = transcript_json.get("chunks", [])
    if not chunks:
        return 0

    if overwrite:
        existing = collection.get(where={"video_id": video_id})
        if existing and existing.get("ids") and len(existing["ids"]) > 0:
            collection.delete(ids=existing["ids"])

    docs_to_add = []
    metas_to_add = []
    ids_to_add = []

    for idx, chunk in enumerate(chunks):
        raw_text = chunk.get("text", "")
        start = float(chunk.get("start", 0.0) or 0.0)
        end = float(chunk.get("end", 0.0) or 0.0)

        # Context-enriched document text for multilingual semantic embedding
        context_parts = []
        if title:
            context_parts.append(title)
        if category:
            context_parts.append(category)
        if raw_text:
            context_parts.append(raw_text)
        enriched_text = ". ".join(context_parts) if context_parts else raw_text

        metadata = {
            **base_metadata,
            "start": start,
            "end": end,
            "raw_text": raw_text
        }
        vid = f"{video_id}_{idx}"
        docs_to_add.append(enriched_text)
        metas_to_add.append(metadata)
        ids_to_add.append(vid)

    collection.add(
        documents=docs_to_add,
        metadatas=metas_to_add,
        ids=ids_to_add,
    )
    return len(docs_to_add)

def transcript_exists(video_id, collection):
    existing_docs = collection.get(
        where={"video_id": video_id}
    )
    return len(existing_docs['ids']) > 0

def main():
    host, collection_name, path, overwrite = get_args()
    print(f"Connecting to ChromaDB at host '{host}', port 8000...")
    client = chromadb.HttpClient(host=host, port=8000)
    use_ef = ef.get_embedding_function()

    collection = client.get_or_create_collection(name=collection_name, embedding_function=use_ef)
    print(f"Using collection: {collection_name} (current count: {collection.count()})")
    print(f"Reading transcripts from: {path}")

    files = [f for f in sorted(os.listdir(path)) if f.endswith(".json")]
    total_added = 0
    for file in files:
        filepath = os.path.join(path, file)
        with open(filepath, "r", encoding="utf-8") as input_file:
            json_input = json.load(input_file)
            vid = json_input.get("id")
            if not overwrite and transcript_exists(vid, collection):
                print(f"Transcript {vid} already exists in collection. Skipping.")
                continue

            print(f"Indexing transcript {vid}: {json_input.get('title', '')[:50]}...")
            num_chunks = add_transcript(json_input, collection, overwrite=overwrite)
            print(f"  -> Added {num_chunks} chunks for {vid}.")
            total_added += 1

    print(f"Done! Updated {total_added} transcripts in collection '{collection_name}'. New total items: {collection.count()}")

if __name__ == "__main__":
    main()






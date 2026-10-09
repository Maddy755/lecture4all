"""Index transcript chunks into a separate Chroma collection using multilingual E5."""
import json
from pathlib import Path
import chromadb
from embedding_function_e5 import E5Encoder

CHROMA_HOST = "chromadb"
CHROMA_PORT = 8000
COLLECTION_NAME = "w4a-multilingual-e5"
TRANSCRIPT_DIR = Path("/processed_transcripts")
BATCH_SIZE = 32

def priority(path: Path) -> int:
    if path.name.endswith("_transcript_fixed.json"):
        return 0
    if path.name.endswith("_transcript_new.json"):
        return 2
    return 1

def main():
    if not TRANSCRIPT_DIR.exists():
        raise FileNotFoundError(f"Transcript directory not mounted: {TRANSCRIPT_DIR}")

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    encoder = E5Encoder()
    seen_video_ids = set()
    videos_added = chunks_added = 0

    paths = sorted(TRANSCRIPT_DIR.glob("*.json"), key=lambda p: (priority(p), p.name.lower()))
    paths = [p for p in paths if not p.name.endswith("_transcript_new.json")]

    for path in paths:
        try:
            with path.open("r", encoding="utf-8") as f:
                transcript = json.load(f)
        except Exception as exc:
            print(f"Skipping unreadable {path.name}: {exc}")
            continue

        video_id = str(transcript.get("id", "")).strip()
        chunks = transcript.get("chunks", [])
        if not video_id or not isinstance(chunks, list) or not chunks:
            print(f"Skipping unsupported/empty transcript: {path.name}")
            continue
        if video_id in seen_video_ids:
            print(f"Skipping duplicate transcript for {video_id}: {path.name}")
            continue
        seen_video_ids.add(video_id)

        existing = collection.get(where={"video_id": video_id}, include=[])
        if existing.get("ids"):
            print(f"Already indexed: {video_id}; skipping.")
            continue

        base_metadata = {
            "video_id": video_id,
            "title": str(transcript.get("title", video_id)),
            "speaker": str(transcript.get("speaker", "")),
            "date": str(transcript.get("date", "")),
            "category": str(transcript.get("category", "")),
            "thumbnail_url": str(transcript.get("thumbnail", "")),
            "m3u8_url": str(transcript.get("m3u8", "")),
        }
        valid = []
        for chunk in chunks:
            text = str(chunk.get("text", "")).strip()
            if not text:
                continue
            try:
                start = float(chunk.get("start", 0))
                end = float(chunk.get("end", start))
            except (TypeError, ValueError):
                start, end = 0.0, 0.0
            valid.append((text, start, end))
        if not valid:
            print(f"No usable chunks in {path.name}")
            continue

        for offset in range(0, len(valid), BATCH_SIZE):
            batch = valid[offset:offset + BATCH_SIZE]
            texts = [item[0] for item in batch]
            embeddings = encoder.encode_passages(texts)
            ids = [f"{video_id}_chunk_{offset+i:05d}" for i in range(len(batch))]
            metadatas = [
                {**base_metadata, "start": start, "end": end}
                for _, start, end in batch
            ]
            collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
            chunks_added += len(batch)

        videos_added += 1
        print(f"Indexed {video_id}: {len(valid)} chunks")

    print(f"\nCollection: {COLLECTION_NAME}")
    print(f"New videos indexed: {videos_added}")
    print(f"New chunks indexed: {chunks_added}")
    print(f"Total collection records: {collection.count()}")

if __name__ == "__main__":
    main()

"""Search the separate E5 collection without modifying the original query.py."""
import chromadb
from embedding_function_e5 import E5Encoder

CHROMA_HOST = "chromadb"
CHROMA_PORT = 8000
COLLECTION_NAME = "w4a-multilingual-e5"

def search(query_text: str, n_results: int = 10):
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(name=COLLECTION_NAME)
    count = collection.count()
    if count == 0:
        return []

    encoder = E5Encoder()
    query_embedding = encoder.encode_queries([query_text])[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, count),
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "id": result["ids"][0][i],
            "text": result["documents"][0][i],
            "metadata": result["metadatas"][0][i],
            "distance": result["distances"][0][i],
        }
        for i in range(len(result["ids"][0]))
    ]

def main():
    query = input("Enter a query in any language: ").strip()
    if not query:
        print("Empty query.")
        return
    for rank, row in enumerate(search(query, 10), start=1):
        meta = row["metadata"] or {}
        print("=" * 72)
        print(f"{rank}. {meta.get('title', meta.get('video_id', 'Unknown'))}")
        print(f"Video ID: {meta.get('video_id')} | Distance: {row['distance']:.4f}")
        print(f"Timestamp: {meta.get('start', 0)} - {meta.get('end', 0)} seconds")
        print(row["text"])

if __name__ == "__main__":
    main()

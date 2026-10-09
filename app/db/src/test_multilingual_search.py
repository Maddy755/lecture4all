import chromadb
import tensorflow_text
import tensorflow_hub as hub
import os

os.environ["TFHUB_CACHE_DIR"] = "/db/src/tfhub_cache"

class USEEmbeddingFunction:
    def __init__(self):
        self.model_url = (
            "https://tfhub.dev/google/"
            "universal-sentence-encoder-multilingual/3"
        )
        self.embed = hub.load(self.model_url)

    def __call__(self, input):
        return self.embed(input).numpy()


client = chromadb.HttpClient(
    host="chromadb",
    port=8000
)

embedding_function = USEEmbeddingFunction()

collection = client.get_collection(
    name="w4a-v2",
    embedding_function=embedding_function
)

queries = [
    "What is DBMS?",
    "DBMS क्या है?",
    "தரவுத்தளம் என்றால் என்ன?"
]

for query in queries:

    print("\n" + "=" * 60)
    print("QUERY:", query)
    print("=" * 60)

    result = collection.query(
        query_texts=[query],
        n_results=10
    )

    for i in range(len(result["ids"][0])):

        metadata = result["metadatas"][0][i]
        document = result["documents"][0][i]

        print(
            f"\n{i + 1}. "
            f"{metadata.get('title')} "
            f"[{metadata.get('video_id')}]"
        )

        print(
            f"Distance: {result['distances'][0][i]}"
        )

        print(
            f"Text: {document[:250]}"
        )
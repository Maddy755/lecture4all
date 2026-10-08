import chromadb
import json
import os
from chromadb.utils import embedding_functions
import tensorflow_text
import tensorflow_hub as hub

os.environ["TFHUB_CACHE_DIR"] = "/db/src/tfhub_cache"

#model="all-mpnet-base-v2"

class USEEmbeddingFunction:
    def __init__(self):
        # Load the USE Large model
        self.model_url = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
        self.embed = hub.load(self.model_url)

    def __call__(self, input: list[str]) -> list[list[float]]:
        # Generate embeddings for the input texts
        return self.embed(input).numpy()

def get_embedding_function():
    use_embedding_function = USEEmbeddingFunction()
    return use_embedding_function
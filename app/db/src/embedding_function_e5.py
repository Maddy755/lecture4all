"""Separate E5 encoder; leaves the existing USE encoder unchanged."""
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-base"

class E5Encoder:
    def __init__(self, model_name: str = MODEL_NAME):
        # CPU avoids CUDA initialization issues in this Docker environment.
        self.model = SentenceTransformer(model_name, device="cpu")

    def encode_passages(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            [f"passage: {text}" for text in texts],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def encode_queries(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            [f"query: {text}" for text in texts],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

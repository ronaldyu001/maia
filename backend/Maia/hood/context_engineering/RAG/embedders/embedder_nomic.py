from sentence_transformers import SentenceTransformer


class NomicEmbedder():
    """
    Constructor Arguments
    - model_name: str = "nomic-ai/nomic-embed-text-v1.5"

    Member Variables
    - model
    - dimensions

    Member Functions
    - encode
    """
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1.5"):
        # ----- Creates model and gets dimensions -----
        self.model = SentenceTransformer(
            model_name_or_path=model_name, 
            trust_remote_code=True,
            device="cpu",
            revision="e5cf08aadaa33385f5990def41f7a23405aec398"
        )
        self.dimensions = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> list[list[float]]:
        """
        Arguments
        - list of strings to embed
        
        Returns
        - list of vectors
        """
        # normalized embeddings → use FAISS inner product as cosine similarity
        return self.model.encode(texts, normalize_embeddings=True).tolist()

from backend.context_engineering.RAG.embedders.embedder_nomic import NomicEmbedder
from backend.context_engineering.RAG.helpers.generic.normalize_data import normalize_embed_input


class faiss_retriever():
    def __init__(self):
        self.embedder = NomicEmbedder()

    def retrieve_vectors(self, query: str) -> str:
        """
        Arguments
        -

        Returns
        -
        """
        try:
            # --- normalize and embed data ---
            query = normalize_embed_input(query=query)
            _vectorized_query = self.embedder.encode(texts=query)
            vectorized_query = 

            # ---  ---

            return True
        

        except:
            return False
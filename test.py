from sentence_transformers import SentenceTransformer
m = SentenceTransformer("intfloat/e5-base-v2", device="cpu")
print("dim:", m.get_sentence_embedding_dimension())
print("vec:", m.encode(["hi"]).shape)
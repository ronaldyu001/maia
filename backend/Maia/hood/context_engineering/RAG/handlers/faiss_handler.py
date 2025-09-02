import faiss, json, uuid, numpy as np
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal, Optional

from backend.context_engineering.RAG.helpers.generic.normalize_data import normalize_embed_input, normalize_meta_input
from backend.context_engineering.helpers.uuid4_to_int64 import uuids_to_ids64
from backend.tools.generic._time import time_now
from backend.context_engineering.RAG.embedders.embedder_nomic import NomicEmbedder


# ===== Schemas =====
class MetaData( BaseModel ):
    """
    Schema for each vector's metadata.

    Required Arguments
    - id: auto-generated uuid4
    - data: the text being stored in the vector
    - topics: list of topics related to the data
    - collection: source of data. e.g.( conversations, goals, facts )

    Optional Arguments
    - session_id: conversation session id of data
    - title: brief title of data
    - importance: manually given rating of importance (0 - 1). 0 is not important.
    """
    # ----- required fields -----
    id: str
    session_id: Optional[str] = None
    data: str
    collection: Literal["conversations", "goals", "facts"]
    created_at: str = Field(default_factory=time_now)

    # ----- optional fields -----
    topics: list[str] = Field(default_factory=list)
    title: Optional[str] = None
    importance: Optional[float] = None


# ===== Handler =====
class FaissHandler():
    """
    The constructor loads:
    - self.meta_paths: dict[str, Path]
    - self.index_paths: dict[str, Path]
    - self.map_path: Path
    - self.embedder: NomicEmbedder
    - self.dimensions: int
    - self.index = None
    - self.metadata = []
    - self.map = {}
    """
    # ===== Constructor =====
    def __init__(
        self,
        index_path="backend/memory/embedded/faiss",
        metadata_path="backend/memory/embedded/metadata",
    ):
        # -----  set paths -----
        print(f"- Setting paths...")
        self.meta_paths = {
            "facts": Path(metadata_path) / "facts",
            "goals": Path(metadata_path) / "goals",
            "conversations": Path(metadata_path) / "conversations"
        }
        self.index_paths = {
            "facts": Path(index_path) / "facts.faiss",
            "goals": Path(index_path) / "goals.faiss",
            "conversations": Path(index_path) / "conversations.faiss",
        }
        self.map_path = self.meta_paths["conversations"] / "map.json"   # map only needed for conversations

        # ----- create folders if DNE -----
        print(f"- Building/Verifying memory file structure...")
        for meta_path, index_path in zip(self.meta_paths.values(), self.index_paths.values()):
            meta_path.mkdir(parents=True, exist_ok=True)
            index_path.parent.mkdir(parents=True, exist_ok=True)
        self.map_path.parent.mkdir(parents=True, exist_ok=True)

        # ----- load embedder -----
        print(f"- Loading embedder and getting dimensions...")
        self.embedder = NomicEmbedder()
        self.dimensions =   getattr(self.embedder, "dimensions", None) or \
                            self.embedder.model.get_sentence_embedding_dimension()
        
        # ----- instantiate other members -----
        self.metadata = []
        self.map = {}


    # ===== Function: add vector =====
    def add_vector(
        self, 
        data: list[str], 
        collection: Literal["conversations", "goals", "facts"],
        metadata: list[dict] | None = None, 
        session_id: str | None = None,
    ):
        """
        Arguments
        - data: list of string(s) to vectorize (each string becomes a vector).
        - collection: source of data.
        - session_id: optionally provide a session id. Will include in metadata if provided.
        - metadata: optionally provide metadata for data. Will override given collection and sesssion_id.
        """
        try:
            # --- load index, metadata, and map ---
            # load index
            print(f"- Loading index...")
            if self.index_paths[collection].exists(): 
                self.index = faiss.read_index(str(self.index_paths[collection]))
            else:
                index = faiss.IndexFlatIP(self.dimensions)
                self.index = faiss.IndexIDMap2(index)

            # load metadata and map if needed
            print(f"- Loading metadata...")
            if collection == "conversations":
                metadata_path = self.meta_paths["conversations"]
                print(f"- Loading map...")
                if not self.map_path.exists(): self.map = {}
                else: self.map = json.loads(str(self.map_path).read_text())
            else: metadata_path = self.meta_paths[collection]

            # --- normalize data ---
            print(f"- Normalizing data...")
            data = normalize_embed_input(query=data)
            metadata = normalize_meta_input(metadata=metadata, data=data)

            # --- create vectors and ids ---
            print(f"- Creating vectors...")
            # create vectors
            vectors = self.embedder.encode(texts=data)
            print(f"- Creating uuids...")
            # create uuids and ids
            uuids = [str(uuid.uuid4()) for _ in data]
            print(f"- Creating ids...")
            ids = uuids_to_ids64(uuid_list=uuids)

            # -- vectors: float32, 2D, contiguous
            vectors = np.asarray(vectors, dtype=np.float32)
            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)
            vectors = np.ascontiguousarray(vectors)
            # If you intend cosine similarity with IndexFlatIP, normalize:
            faiss.normalize_L2(vectors)
            # -- ids: int64, 1D, contiguous, non-negative, unique
            ids = np.asarray(ids, dtype=np.int64).reshape(-1)
            ids = np.ascontiguousarray(ids)

            # --- add vectors and ids mapped index ---
            print(f"- Updating mapped index...")
            self.index.add_with_ids(vectors, ids)

            # --- set metadata path, defaults to conversational ---
            print(f"- Setting paths and loading metadata if needed...")
            metadata_path = self.meta_paths["conversations"] / f"{session_id}.json"

            if collection != "conversations":
                print(f"    - Loading metadata...")
                metadata_path = self.meta_paths[collection]
                try: self.metadata = json.loads(metadata_path.read_text())
                except Exception as err:
                    print(f"- Unable to load metadata. Creating new list...")
                    self.metadata = []

            # --- update map if applicable ---
            print(f"- Updating map...")
            if collection == "conversations":
                for _uuid, _index in zip(uuids, ids):
                    self.map[_index] = session_id if collection == "conversations" else collection

            # --- update metadata (prev metadata grabbed earlier if applicable) ---
            print(f"- Updating metadata...")

            # get new metadata
            for _entry, _uuid, _meta in zip(data, uuids, metadata):
                # load given metadata
                try: 
                    print(f"    - Metadata found, loading...")
                    row_metadata = MetaData(**_meta)
                    self.metadata.append(row_metadata)
                
                # if metadata not able to be loaded, manually fill
                except Exception as err: 
                    print(f"    - No metadata loaded. Generating...")
                    row_metadata =  MetaData(
                                        id=str(_uuid),
                                        session_id=session_id,
                                        data=_entry,
                                        collection=collection
                                    )
                    print(f"    - Generated metadata. Adding metadata to list...\n")
                    self.metadata.append(row_metadata.model_dump())

            # --- updating core files ---
            print(f"- Writing index file...")
            faiss.write_index(self.index, str(self.index_paths[collection]))

            print(f"- Writing metada file...")
            metadata_path.write_text(json.dumps(self.metadata))

            if collection == "conversations":
                print(f"- Writing map file...")
                # Numpy int64 variable type needs to be converted to int to write
                clean_map = {int(k): str(v) for k, v in self.map.items()}
                self.map_path.write_text(json.dumps(clean_map, ensure_ascii=False, indent=2))

            return True

        except Exception as err:
            return False
        

    


    def reset(self):
        """
        Fully resets all member variables of the FaissHandler.
        """
        self.dimensions =   getattr(self.embedder, "dimensions", None) or \
                            self.embedder.model.get_sentence_embedding_dimension()
        self.metadata = []
        self.index = faiss.IndexFlatIP(self.dimensions)
        self.map = faiss.IndexIDMap2(self.index)
        return
    


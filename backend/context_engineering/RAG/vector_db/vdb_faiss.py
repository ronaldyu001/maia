import faiss, json, uuid, numpy as np
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal, Optional

from backend.context_engineering.helpers.uuid4_to_int64 import uuids_to_ids64
from backend.tools.memory.storage import load_json
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
    """
    # ===== Constructor =====
    def __init__(
        self,
        index_path="backend/memory/embedded/faiss/index.faiss",
        map_path="backend/memory/embedded/faiss/map.json",
        metadata_path="backend/memory/processed/",
    ):
        # -----  set paths -----
        print(f"- Setting paths...")
        self.gen_meta_paths = {
            "facts": Path(metadata_path) / "facts.json",
            "goals": Path(metadata_path) / "goals.json"
        }
        self.core_paths = {
            "index": Path(index_path),
            "map": Path(map_path)
        }
        self.conversational_meta_path = Path(metadata_path) / "conversations"

        # ----- create files if DNE -----
        print(f"- Checking core file paths...")
        for _path in self.core_paths.values():
            _path.parent.mkdir(exist_ok=True)
        self.conversational_meta_path.mkdir(parents=True, exist_ok=True)

        # ----- load embedder -----
        print(f"- Loading embedder and getting dimensions...")
        self.embedder = NomicEmbedder()
        self.dimensions =   getattr(self.embedder, "dimensions", None) or \
                            self.embedder.model.get_sentence_embedding_dimension()
    
        # ----- load index -----
        index_path = self.core_paths["index"] / "index.faiss"
        if index_path.exists():
            print(f"- Index found, loading...")
            # reloads vectors from index.faiss
            self.index = faiss.read_index(index_path)
        else:
            print(f"- Index not found, creating new one...")
            # if index.faiss DNE, create blank index with correct dimensions
            self.index = faiss.IndexFlatIP(self.dimensions)  # cosine if normalized

        # ----- load map -----
        map_path = self.core_paths["map"] / f"map.json"
        if map_path.exists():
            print(f"- Map found, loading...")
            # reloads vectors from index.faiss
            self.map = json.loads(map_path.read_text())
        else:
            print(f"- Map not found, creating new one...")
            # if index.faiss DNE, create blank index with correct dimensions
            self.map = {}

        # ----- create mapped index -----
        # wraps the index with a map layer
        self.mapped_index = faiss.IndexIDMap2(self.index)

        # ----- create metadata -----
        self.metadata = []


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
            # --- normalize input to list ---
            print(f"- Normalizing inputs...")
            data = [data] if isinstance(data, str) else list(data)
            if not data:
                raise ValueError("No texts to embed.")

            # --- metadata length should equal input length ---
            print(f"- Aligning metadata...")
            if metadata is None:
                metadata = [{} for _ in data]
            if len(metadata) != len(data):
                raise ValueError("metadata length must match texts length.")

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
            self.mapped_index.add_with_ids(vectors, ids)

            # --- set metadata path, defaults to conversational ---
            print(f"- Setting paths and loading metadata if needed...")
            print(collection, self.gen_meta_paths)
            metadata_path = self.conversational_meta_path / f"{session_id}.json"

            if collection != "conversations":
                print(f"    - Loading metadata...")
                metadata_path = self.gen_meta_paths[collection]
                try: self.metadata = json.loads(metadata_path.read_text())
                except Exception as err:
                    print(f"- Unable to load metadata. Creating new list...")
                    self.metadata = []


            # --- load map ---
            print(f"- Loading map...")
            try:
                # load map from file
                map_path = self.core_paths["map"]
                self.map = json.loads(map_path.read_text())
            except Exception as err:
                # load blank map if load from files fails
                print(f"ERROR: {err}\n-Loading new map...")
                self.map = {}

            # --- update map ---
            print(f"- Updating map...")
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

            # --- writing core files ---
            print(f"- Writing index file...")
            if not self.core_paths["index"].exists(): self.core_paths["index"].touch()
            faiss.write_index(self.mapped_index, str(self.core_paths["index"]))

            print(f"- Writing metada file...")
            metadata_path.write_text(json.dumps(self.metadata))

            print(f"- Writing map file...")
            # Numpy int64 variable type needs to be converted to int to write
            clean_map = {int(k): str(v) for k, v in self.map.items()}
            self.core_paths["map"].write_text(json.dumps(clean_map, ensure_ascii=False, indent=2))

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
    


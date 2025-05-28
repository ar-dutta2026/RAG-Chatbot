"""
ingest.py

Downloads and indexes the rag-mini-wikipedia dataset into a local ChromaDB vector store.

This script:
  1. Loads the "rag-mini-wikipedia" text-corpus from HuggingFace.
  2. Dynamically identifies the text column (non-"id").
  3. Iterates over each passage, encodes it using a SentenceTransformer model,
     and writes (id, embedding, text) into the "wiki" collection in ChromaDB.
  4. Logs progress every 1000 documents.

Usage:
    python ingest.py
"""
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from tools.config import CHROMA_DB_DIR, EMBEDDING_MODEL

def main():
    """
    Main entry point for ingestion:
    - Loads dataset
    - Initializes embedder and ChromaDB collection
    - Encodes and indexes each passage
    """
    # 1. Load the passages split from the rag-mini-wikipedia dataset
    ds = load_dataset(
        "rag-datasets/rag-mini-wikipedia",
        "text-corpus",
        split="passages"
    )

    # 2. Initialize the SentenceTransformer model for embeddings
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    # 3. Determine which column contains the text (ignore 'id')
    text_col = next(c for c in ds.column_names if c.lower() != "id")
    print(f"Indexing `{text_col}` as document")

    # 4. Connect to or create the ChromaDB collection
    client = PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_or_create_collection(name="wiki")

        # Step 5: Iterate over dataset and index
    for idx, item in enumerate(ds):
        try:
            # Extract raw text for embedding
            text = item[text_col]
            # Compute embedding vector (list of floats)
            embedding = embedder.encode(text).tolist()
            # Add to ChromaDB: id, embedding, and raw document
            collection.add(
                ids=[str(idx)],
                embeddings=[embedding],
                documents=[text]
            )
        except Exception as e:
            # On error, log and proceed with next item
            print(f"Error indexing doc at index {idx}: {e}")
            continue

        # Progress logging for large datasets
        if idx > 0 and idx % 1000 == 0:
            print(f"Indexed {idx} documents so far...")

    # Final confirmation
    print("Indexing complete.")


if __name__ == "__main__":
    main()

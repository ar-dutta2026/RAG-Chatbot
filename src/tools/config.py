"""
config.py

Configuration settings for the RAG Chat application:

- CHROMA_DB_DIR:      Filesystem path to your local ChromaDB vector store.
- EMBEDDING_MODEL:    HuggingFace sentence-transformers model for query/document embeddings.
- OPENAI_API_KEY:     Retrieved from the environment; used to authenticate OpenAI API calls.
- OPENAI_MODEL:       The ChatCompletion model to use.
- TOP_P, TEMPERATURE: Sampling parameters controlling response creativity.
"""

import os

# ChromaDB Vector Store

# Path to your local ChromaDB directory.
# ChromaDB will persist/load embeddings and documents here.
CHROMA_DB_DIR: str = "./chroma_db"

# HuggingFace embedding model name.
# Used by sentence-transformers to encode queries & documents.
EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"


# OpenAI ChatCompletion Settings

# Your OpenAI API key; read from environment to avoid hardcoding secrets.
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# OpenAI ChatCompletion model name (e.g. gpt-3.5-turbo or gpt-4).
OPENAI_MODEL: str = "gpt-3.5-turbo"

# Sampling configuration:
# - top_p: nucleus sampling cumulative probability threshold.
# - temperature: controls randomness (higher = more creative).
TOP_P: float = 0.9
TEMPERATURE: float = 0.8

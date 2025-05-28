"""
utils.py

Core utility functions for embedding queries, retrieving context from ChromaDB,
and constructing prompts for the RAG-based chatbot.

This module:
  1. Lazily loads a sentence-transformer embedding model.
  2. Connects to the ChromaDB collection storing embedded documents.
  3. Retrieves top-k relevant context passages for a given query.
  4. Builds a message list that combines system rules, history, and current user input.
"""
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import re
from chromadb.config import Settings
from tools.config import CHROMA_DB_DIR, EMBEDDING_MODEL

# Global cache variables to avoid re-instantiating on each call
_embedder  = None
_client    = None
_collection = None

def get_embedder():
    """
    Load and cache the sentence-transformer embedding model if not already loaded.
    Returns:
        SentenceTransformer: The embedding model instance.
    """

    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder

def get_collection():
    """
    Connect to ChromaDB and access the 'wiki' collection. Creates it if it doesn't exist.
    Returns:
        Collection: A ChromaDB collection instance for querying documents.
    """

    global _client, _collection
    if _client is None:
        _client = PersistentClient(path=CHROMA_DB_DIR)
        _collection = _client.get_or_create_collection("wiki")
    return _collection

def retrieve_context(query: str, k: int = 3):
    """
    Retrieve top-k relevant documents from ChromaDB given a natural language query.

    Args:
        query (str): The user query to embed and retrieve matches for.
        k (int): The number of top results to return. Default is 3.

    Returns:
        list[str]: A list of top-k document strings relevant to the query.
    """

    # Convert query to embedding
    emb     = get_embedder().encode(query).tolist()

    # Query ChromaDB using vector similarity
    results = get_collection().query(query_embeddings=[emb], n_results=k)

    return results["documents"][0]

def build_prompt(history: list[dict], context: list[str], user_query: str) -> list[dict]:
    """
    Construct the full message list for the OpenAI Chat API including:
    - System prompt with RAG constraints
    - All previous chat history
    - The new user input

    Args:
        history (list[dict]): Full conversation history with 'user' and 'assistant' turns.
        context (list[str]): Retrieved context passages from ChromaDB.
        user_query (str): The current question from the user.

    Returns:
        list[dict]: A list of message dicts formatted for OpenAI's chat endpoint.
    """

     # Define system-level instructions for the assistant's behavior
    system = """\
You are a friendly, conversational assistant that always considers the full chat history.

1) If the user simply greets you (“hi”, “hello”, “hey”), reply exactly:
   “Hello! How can I assist you today?”
2) If the user asks a meta‐question about our conversation 
   (e.g. “what did I just ask?”, “what questions have I asked?”), answer from the prior turns.
3) Otherwise, for any factual question, answer only from the context below. 
   If the answer cannot be found there, reply exactly:
   
Always paraphrase and speak naturally—do not quote verbatim.

---
Context:
""" + "\n\n".join(context)

    # Begin message list with system instructions
    messages = [{"role": "system", "content": system}]

    # Add all prior chat history (alternating user/assistant turns)
    for turn in history:
        messages.append({
            "role":    turn["role"],
            "content": turn["content"]
        })

    # Add the user's current query as the final message
    messages.append({"role": "user", "content": user_query})
    return messages

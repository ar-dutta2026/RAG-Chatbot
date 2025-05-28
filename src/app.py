# app.py
# 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
"""
app.py

Flask application for a Retrieval-Augmented Generation (RAG) chatbot.

This script:
  1. Serves the frontend (static/index.html) on GET '/'.
  2. Handles POST '/api/chat': accepts JSON { history, query }.
  3. Retrieves top-3 context passages from ChromaDB.
  4. Constructs the conversation prompt with system instructions, full history, and context.
  5. Calls OpenAI ChatCompletion API and returns the assistant's reply as JSON.

Usage:
    export OPENAI_API_KEY="your-key"
    python app.py
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from tools.config import OPENAI_API_KEY, OPENAI_MODEL, TOP_P, TEMPERATURE
from tools.utils import retrieve_context, build_prompt

# Disable PyTorch compile optimizations if needed
os.environ["TORCH_COMPILE_DISABLE"] = "1"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create Flask app, serve files from static/
app = Flask(__name__, static_folder="static")

@app.route("/", methods=["GET"])
def index():
    """
    Serve the main chatbot interface HTML page.
    
    Returns:
        Response: The HTML page loaded from /static/index.html
    """
    return send_from_directory("static", "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Process a POST request to the chatbot API.
    
    Steps:
      1. Parse the incoming JSON payload.
      2. Retrieve the top-3 relevant passages using vector similarity.
      3. Build the chat prompt including system, context, and full history.
      4. Call OpenAI's ChatCompletion endpoint.
      5. Return the generated assistant response as JSON.

    Returns:
        Response: JSON containing the assistant's reply.
    """
    # Parse the request JSON payload
    payload = request.json or {}
    history = payload.get("history", [])  # previous turns
    query = payload.get("query", "")     # current user query

    # Retrieve top-3 relevant documents from ChromaDB
    context_snippets = retrieve_context(query, k=3)
    print(f"Retrieved context for '{query}':", context_snippets)

    # Build full chat prompt for the OpenAI model
    messages = build_prompt(history, context_snippets, query)

    # Generate a response from OpenAI's ChatCompletion API
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )
    reply = completion.choices[0].message.content.strip()

    # Send the assistant's reply back to the frontend
    return jsonify({"response": reply})

if __name__ == "__main__":
    # Run the Flask development server on http://127.0.0.1:5000
    app.run(port=5000, debug=True)

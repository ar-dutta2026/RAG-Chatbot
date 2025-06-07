# RAG Chatbot

This project implements a **Retrieval-Augmented Generation (RAG)** chatbot using OpenAI's ChatCompletion API. It combines real-time user interaction with contextual document retrieval, enabling the chatbot to provide factually grounded and coherent answers over multi-turn conversations.

### What It Does:
- Maintains full conversational history to support contextually rich responses.
- Automatically expands pronoun-based follow-up questions using prior user queries.
- Retrieves semantically relevant documents from a local vector database built on a Mini Wikipedia dataset.
- Uses this retrieved context to construct a prompt sent to the OpenAI API for response generation.


## Setup
1. **Clone the Repo**
```bash
git clone https://github.com/ar-dutta2026/RAG-Chatbot.git
```   

2. **Install dependencies**  
```bash
pip install -r requirements.txt
```

3. **Move into the src Folder**
```bash
cd src
```

4. **Export the OpenAPI key**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

5. **Index the RAG Dataset**
```bash
python3 ingest.py
```

6. **Start the Flask Server**
```bash
python3 app.py
```

Once running, open your browser to http://127.0.0.1:5000 (localhost) to chat away with the Chatbot!

 
## Architecture

### 1. Frontend (HTML/CSS/JavaScript)
- Renders an iMessage-style chat UI with:
  - Typewriter animation for Chatbot responses.
  - A pre-generated greeting message on load.
- Sends user queries and chat history to the backend via a `POST` request.
- Displays the Chatbot's response with animation inside a styled message bubble.

---

### 2. Backend (Flask)
- Flask web server exposing the route:
  ```
  POST /api/chat
  ```
- Accepts JSON data:
  ```json
  {
    "history": [{"role": "user", "content": "..."}, ... ],
    "query": "User question here"
  }
  ```

---

### 3. Retrieval System (RAG Integration)
- Uses the function `retrieve_context(query, k=3)` to perform **semantic similarity search** over a local **Chroma vector database**.
- Embedding model used: 
  ```
  sentence-transformers/all-MiniLM-L6-v2
  ```
- Steps:
  1. Embed the user query.
  2. Compare against pre-embedded documents in the vector store.
  3. Return top-k most relevant passages.

---

### 4. Prompt Construction
- A structured prompt is built for the LLM that includes:
  - A **system instruction**:
    ```
    You are a helpful assisstant that ONLY answers questions based on the provided context...
    ```
  - The retrieved context documents.
  - The full chat history.
  - The user’s new query.

---

### 5. Language Model (LLM)
- LLM used: **OpenAI's `gpt-3.5-turbo`** instance.
- Sampling parameters:
  ```python
  temperature = 0.8
  top_p = 0.9
  ```
- Returns a single completion as the Chatbot's response.

---

## Request-Response Flow

```
User Input -> Frontend sends query + history ->
Flask API (/api/chat) -> Context retrieved via RAG ->
Prompt built with system + context + chat ->
LLM generates grounded answer ->
Response returned and rendered with animation
```



## Design Decisions & Tradeoffs

### 1. **Embedding Model & Vector Store (RAG Backend)**
- **Decision**: Used `sentence-transformers/all-MiniLM-L6-v2` for embedding and ChromaDB for storing vectors.
- **Why**: This embedding model offers a good balance between performance and accuracy, and ChromaDB is lightweight, fast, and easy to integrate.
- **Tradeoff**: MiniLM may not capture deep semantic relationships compared to larger models like BGE or OpenAI embeddings. ChromaDB lacks horizontal scalability for large-scale deployments.

### 2. **Document Chunking Strategy**
- **Decision**: Ingested `.txt` files from the RAG Mini Wikipedia dataset and split them into manageable chunks for embedding.
- **Why**: Smaller chunks ensure relevant retrieval and reduce the risk of context window overflows when prompts are constructed.
- **Tradeoff**: If chunks are too small, context may be lost; if too large, irrelevant tokens may dominate or be truncated during generation.

### 3. **Prompt Engineering & Context Injection**
- **Decision**: Injected retrieved context directly into a system prompt template with strict instruction: "ONLY answer using the following context."
- **Why**: Constrains the language model’s generation, ensuring it doesn’t hallucinate or use external knowledge.
- **Tradeoff**: Limits model flexibility. If the context is not sufficient, the model cannot reason beyond it, even if it normally could.

### 4. **Frontend Conversation Tracking (In-Memory Chat History)**
- **Decision**: Maintained chat history on the frontend and sent it with every request for stateless processing.
- **Why**: Keeps backend simple and avoids session management or databases. Enables fast prototyping.
- **Tradeoff**: No persistence across page reloads unless localStorage is used. Model "remembers" history only if it’s sent with every new query.

### 5. **Chabot Personality & Guardrails**
- **Decision**: Added a system prompt guardrail that explicitly prevents the Chatbot from using any information outside the retrieved context.
- **Why**: This enforces strict RAG compliance and prevents false positives when the dataset lacks coverage.
- **Tradeoff**: The Chatbot may not use its external capabilities to answer question, limiting it to the Wikipedia dataset.

### 6. **Frontend UX Enhancements**
- **Decision**: Implemented:
  - A typewriter animation effect for Chatbot's responses.
  - A floating iMessage-style UI with rounded chat bubbles.
  - A pre-seeded greeting message upon page load.
- **Why**: These features make the experience more engaging and intuitive.
- **Tradeoff**: Typewriter rendering introduces a minor delay for Chatbot's responses and requires careful DOM manipulation.

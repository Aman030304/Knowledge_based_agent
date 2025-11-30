# Knowledge Base Agent (RAG System)

A local RAG (Retrieval-Augmented Generation) agent that answers questions based on your documents (PDF, DOCX, TXT).

## Features
- **Document Loading**: Supports PDF, DOCX, and TXT files.
- **Vector Database**: Uses ChromaDB to store document embeddings locally.
- **RAG Pipeline**: Retrieves relevant context and answers questions using OpenAI's GPT models.
- **CLI Interface**: Simple command-line interface for ingestion and chatting.

## Setup

1. **Install Dependencies**
   Ensure you have Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ollama Setup**
   - Install [Ollama](https://ollama.com/).
   - Pull the required models:
     ```bash
     ollama pull llama3
     ollama pull nomic-embed-text
     ```
   - Ensure Ollama is running (`ollama serve`).

3. **Environment Variables**
   - No API keys needed for Ollama!
   - (Optional) You can keep `.env` for other configs if needed.

## Usage

1. **Run the Agent**
   ```bash
   python main.py
   ```

2. **Ingest Documents**
   - Select Option `1` in the menu.
   - Place your documents in the `docs/` folder (created automatically if missing).
   - Press Enter to start ingestion.

3. **Chat (CLI)**
   - Select Option `2` in the menu.
   - Ask questions about your documents.
   - Type `exit` to quit.

4. **Run Streamlit App (Web UI)**
   ```bash
   streamlit run app.py
   ```
   - Upload documents via the sidebar.
   - Click "Process Documents".
   - Chat in the main window.

## Project Structure
- `main.py`: Entry point for the CLI.
- `ingest.py`: Handles document loading, splitting, and vector DB creation.
- `rag_pipeline.py`: Sets up the retriever and RAG chain.
- `requirements.txt`: Python dependencies.
- `docs/`: Directory for your source documents.
- `chroma_db/`: Directory where the vector database is stored.

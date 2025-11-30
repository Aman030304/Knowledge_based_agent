import streamlit as st
import os
import ingest
import rag_pipeline
import chat_manager
import requests

st.set_page_config(page_title="Knowledge Base Agent", layout="wide")

def is_ollama_running():
    """Checks if Ollama is running on the default port."""
    try:
        response = requests.get("http://localhost:11434", timeout=1)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def save_uploaded_file(uploaded_file):
    """Saves uploaded file to the docs directory."""
    if not os.path.exists(ingest.DATA_PATH):
        os.makedirs(ingest.DATA_PATH)
    
    file_path = os.path.join(ingest.DATA_PATH, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def main():
    st.title("🤖 Knowledge Base Agent (RAG)")

    if not is_ollama_running():
        st.error("⚠️ **Ollama is not running!**")
        st.markdown("""
        To use this app, you need to have **Ollama** installed and running.
        
        1. **Install Ollama**: [Download here](https://ollama.com/download)
        2. **Start Ollama**: Run `ollama serve` in your terminal or open the Ollama app.
        3. **Pull Models**: Run `ollama pull llama3` and `ollama pull nomic-embed-text`.
        
        Once running, refresh this page.
        """)
        st.stop()

    # Initialize session state for chat ID if not present
    if "current_chat_id" not in st.session_state:
        # Try to load the most recent chat, or create new
        chats = chat_manager.list_chats()
        if chats:
            st.session_state.current_chat_id = chats[0]["id"]
        else:
            st.session_state.current_chat_id = chat_manager.create_new_chat()

    # Load current chat data
    current_chat = chat_manager.load_chat(st.session_state.current_chat_id)
    if not current_chat:
        # Fallback if file missing
        st.session_state.current_chat_id = chat_manager.create_new_chat()
        current_chat = chat_manager.load_chat(st.session_state.current_chat_id)

    # Sidebar
    with st.sidebar:
        st.header("Document Ingestion")
        uploaded_files = st.file_uploader(
            "Upload PDF, DOCX, or TXT files", 
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True
        )
        
        if st.button("Process Documents"):
            if uploaded_files:
                with st.spinner("Ingesting documents..."):
                    for uploaded_file in uploaded_files:
                        save_uploaded_file(uploaded_file)
                    
                    try:
                        docs = ingest.load_documents(ingest.DATA_PATH)
                        if docs:
                            chunks = ingest.split_text(docs)
                            ingest.create_vector_db(chunks)
                            st.success(f"Successfully processed {len(uploaded_files)} files!")
                        else:
                            st.error("Failed to load documents.")
                    except Exception as e:
                        st.error(f"An error occurred during ingestion: {e}")
                        st.info("Please check your Google API Key and Quota limits.")
            else:
                st.warning("Please upload files first.")

        st.markdown("---")
        st.header("Chat History")
        
        if st.button("➕ New Chat"):
            st.session_state.current_chat_id = chat_manager.create_new_chat()
            st.rerun()

        # List existing chats
        chats = chat_manager.list_chats()
        for chat in chats:
            # Highlight current chat
            label = chat["name"]
            if chat["id"] == st.session_state.current_chat_id:
                label = f"👉 {label}"
            
            if st.button(label, key=f"chat_{chat['id']}"):
                st.session_state.current_chat_id = chat["id"]
                st.rerun()

        st.markdown("---")
        st.header("Chat Options")
        
        # Rename Chat
        new_name = st.text_input("Rename Chat", value=current_chat["name"])
        if st.button("Update Name"):
            if new_name.strip():
                chat_manager.rename_chat(st.session_state.current_chat_id, new_name)
                st.success("Renamed!")
                st.rerun()

        # Delete Chat
        if st.button("🗑️ Delete Chat", type="primary"):
            chat_manager.delete_chat(st.session_state.current_chat_id)
            # Switch to another chat or create new
            remaining_chats = chat_manager.list_chats()
            if remaining_chats:
                st.session_state.current_chat_id = remaining_chats[0]["id"]
            else:
                st.session_state.current_chat_id = chat_manager.create_new_chat()
            st.rerun()

    # Main Chat Interface
    st.subheader(current_chat["name"])
    
    # Initialize messages in session state from loaded chat
    if "messages" not in st.session_state or st.session_state.get("loaded_chat_id") != st.session_state.current_chat_id:
        st.session_state.messages = current_chat["messages"]
        st.session_state.loaded_chat_id = st.session_state.current_chat_id

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            chain = rag_pipeline.get_rag_chain()
            
            if not chain:
                st.error("Vector database not found. Please upload and process documents in the sidebar.")
                response_text = "Please ingest documents first."
            else:
                with st.spinner("Thinking..."):
                    try:
                        result = chain.invoke(prompt)
                        answer = result["answer"]
                        sources = result["context"]
                        
                        response_text = f"{answer}\n\n**Sources:**\n"
                        for i, doc in enumerate(sources):
                            source = os.path.basename(doc.metadata.get("source", "Unknown"))
                            page = doc.metadata.get("page", "N/A")
                            response_text += f"- {source} (Page {page})\n"
                        
                        st.markdown(response_text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        response_text = "I encountered an error."

        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Save chat history
        chat_manager.save_chat(
            st.session_state.current_chat_id, 
            current_chat["name"], 
            st.session_state.messages
        )

if __name__ == "__main__":
    main()

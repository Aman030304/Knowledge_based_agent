import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

CHROMA_PATH = "chroma_db"

def get_retriever():
    """Initializes and returns the ChromaDB retriever."""
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    
    # Check if vector DB exists
    if not os.path.exists(CHROMA_PATH):
        return None
        
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    return db.as_retriever(search_kwargs={"k": 5})

def format_docs(docs):
    """Formats retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    """Creates and returns the RAG chain."""
    retriever = get_retriever()
    if not retriever:
        return None

    template = """You are a helpful assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Use three sentences maximum and keep the answer concise.

    Context:
    {context}

    Question:
    {question}

    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOllama(model="llama3", temperature=0)

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)

    return rag_chain_with_source

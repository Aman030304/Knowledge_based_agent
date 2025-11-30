import os
import sys
import ingest
import rag_pipeline

def main():
    print("Welcome to the Knowledge Base Agent (RAG System)")
    
    while True:
        print("\n--- Menu ---")
        print("1. Ingest Documents")
        print("2. Chat")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n--- Ingesting Documents ---")
            # Create docs folder if it doesn't exist
            if not os.path.exists(ingest.DATA_PATH):
                os.makedirs(ingest.DATA_PATH)
                print(f"Created '{ingest.DATA_PATH}' folder. Please place your documents there.")
                input("Press Enter after you have added documents...")
            
            docs = ingest.load_documents(ingest.DATA_PATH)
            if docs:
                chunks = ingest.split_text(docs)
                ingest.create_vector_db(chunks)
                print("Ingestion complete!")
            else:
                print("No documents found.")
                
        elif choice == "2":
            print("\n--- Chat Mode ---")
            chain = rag_pipeline.get_rag_chain()
            
            if not chain:
                print("Error: Vector database not found. Please ingest documents first (Option 1).")
                continue
                
            print("Type 'exit' or 'quit' to return to the main menu.")
            
            while True:
                query = input("\nYou: ").strip()
                if query.lower() in ["exit", "quit"]:
                    break
                
                if not query:
                    continue
                    
                print("Agent: Thinking...")
                try:
                    result = chain.invoke(query)
                    answer = result["answer"]
                    sources = result["context"]
                    
                    print(f"\nAgent: {answer}")
                    print("\n--- Sources ---")
                    for i, doc in enumerate(sources):
                        source = doc.metadata.get("source", "Unknown")
                        page = doc.metadata.get("page", "N/A")
                        print(f"{i+1}. {os.path.basename(source)} (Page {page})")
                        # print(f"   Content: {doc.page_content[:100]}...") # Optional: show snippet
                except Exception as e:
                    print(f"An error occurred: {e}")
                    
        elif choice == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

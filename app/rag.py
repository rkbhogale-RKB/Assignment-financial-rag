from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sentence_transformers import CrossEncoder

print("Loading model")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#chroma db 
vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

reranker = CrossEncoder( "cross-encoder/ms-marco-MiniLM-L-6-v2")


def process_and_store_document(file_path: str, document_id: int):
   
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    #spliter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)

    
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id

   
    vector_store.add_documents(chunks)
    
    return len(chunks) 

def search_documents(query: str, top_k: int = 20):
    
    results = vector_store.similarity_search(query, k=top_k)
    if not results:
        return []
    pairs=[]
    print(results)
    for doc in results:
        print(doc)
        pairs.append((query, doc.page_content))
    scores = reranker.predict(pairs)
    scored_results = list(zip(results, scores))
    scored_results.sort(key=lambda x: x[1], reverse=True)


    formatted_results = []
    for doc, score in scored_results[:5]:
        formatted_results.append({
            "content": doc.page_content,
            "document_id": doc.metadata.get("document_id", "Unknown"),
            "rerank_score": float(score) 
        })

        
    return formatted_results



def remove_document_embeddings(document_id: int):

    try:

        result = vector_store.get(
            where={"document_id": document_id}
        )

        print("Vector Search Result:", result)

        ids_to_delete = result.get("ids", [])

        # No chunks found
        if not ids_to_delete:
            return 0

        # Delete chunks from ChromaDB
        vector_store.delete(ids=ids_to_delete)

        return len(ids_to_delete)

    except Exception as e:
        print("Error deleting from Vector DB:", e)
        raise e
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


print("Loading model")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#chroma db 
vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

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
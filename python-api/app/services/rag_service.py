from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer
import chromadb
import os

# embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# chromadb persistent client
chroma_client = chromadb.PersistentClient(path="/app/chroma_db")

collection = chroma_client.get_or_create_collection(
    name="documents"
)

# process and store PDF
def process_pdf(file_path: str):

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):

        embedding = embedding_model.encode(
            chunk.page_content
        ).tolist()

        collection.add(
            ids=[f"{os.path.basename(file_path)}_{i}"],
            embeddings=[embedding],
            documents=[chunk.page_content]
        )

    return len(chunks)

# semantic search
def search_documents(query: str, n_results: int = 3):

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0]
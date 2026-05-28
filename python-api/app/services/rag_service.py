import os
import glob
import chromadb

from dotenv import load_dotenv
from openai import OpenAI

from sentence_transformers import SentenceTransformer

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(
    name="documents"
)

# Text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


def ingest_documents():
    documents_path = "/app/documents"

    if not os.path.exists(documents_path):
        return {
            "error": "documents folder not found"
        }

    pdf_files = glob.glob(f"{documents_path}/*.pdf")

    if len(pdf_files) == 0:
        return {
            "error": "no pdf files found"
        }

    all_chunks = []

    for pdf_file in pdf_files:

        pdf_reader = PdfReader(pdf_file)

        text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted

        chunks = text_splitter.split_text(text)

        all_chunks.extend(chunks)

    if len(all_chunks) == 0:
        return {
            "error": "no text extracted"
        }

    embeddings = embedding_model.encode(all_chunks).tolist()

    ids = [f"doc_{i}" for i in range(len(all_chunks))]

    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        ids=ids
    )

    return {
        "message": f"{len(all_chunks)} chunks ingested successfully"
    }


def search_documents(query, n_results=5):

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


def ask_rag(question):

    results = search_documents(question)
    
    print(results)

    documents = results["documents"][0]

    # safeguard in case nothing is found
    if not documents:
        return {
            "answer": "No relevant documents found.",
            "sources": []
        }

    context = "\n\n".join(documents)

    prompt = f"""
You are a helpful AI assistant.

Answer the question ONLY using the context below.
If the answer is not in the context, say:
"I could not find the answer in the provided documents."

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You answer questions using only retrieved document context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": documents
    }
import os
import glob
import chromadb

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from app.services.embedding_service import (
    create_embedding
)

from app.services.openai_service import (
    client
)

from app.services.pdf_service import (
    extract_text_from_pdf
)

# chroma
chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="documents"
)

# splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


def ingest_documents():

    documents_path = "/app/documents"

    pdf_files = glob.glob(
        f"{documents_path}/*.pdf"
    )

    all_chunks = []

    all_metadatas = []

    all_ids = []

    counter = 0

    for pdf_file in pdf_files:

        text = extract_text_from_pdf(pdf_file)

        chunks = text_splitter.split_text(text)

        for chunk in chunks:

            all_chunks.append(chunk)

            all_metadatas.append({
                "source": os.path.basename(pdf_file)
            })

            all_ids.append(f"doc_{counter}")

            counter += 1

    embeddings = [
        create_embedding(chunk)
        for chunk in all_chunks
    ]

    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas,
        ids=all_ids
    )

    return {
        "message": f"{len(all_chunks)} chunks ingested"
    }


def search_documents(query):

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results


def ask_rag(question):

    results = search_documents(question)

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    context = "\n\n".join(documents)

    prompt = f"""
You are an enterprise AI assistant.

Answer ONLY using the context below.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": metadatas
    }
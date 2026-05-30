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

chroma_client = chromadb.PersistentClient(
    path="/app/chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="documents"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300
)

def ingest_documents():

    documents_path = "/app/documents"

    pdf_files = glob.glob(
        f"{documents_path}/*.pdf"
    )

    if not pdf_files:
        return {
            "message": "No PDF files found",
            "chunks": 0
        }

    all_chunks = []
    all_metadatas = []
    all_ids = []

    counter = 0

    for pdf_file in pdf_files:

        pages = extract_text_from_pdf(pdf_file)

        for page_data in pages:

            page_number = page_data["page"]
            page_text = page_data["text"]

            chunks = text_splitter.split_text(page_text)

            for chunk in chunks:

                all_chunks.append(chunk)
               
                all_metadatas.append({
                    "source": os.path.basename(pdf_file),
                    "page": page_number,
                    "chunk": counter
                })

                all_ids.append(
                    f"{os.path.basename(pdf_file)}_page_{page_number}_chunk_{counter}"
                )

                counter += 1

    if not all_chunks:
        return {
            "message": "No text extracted from PDFs",
            "chunks": 0
        }

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
        "message": "Documents ingested successfully",
        "chunks": len(all_chunks)
    }

def search_documents(query):

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=15,
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
    distances = results["distances"][0]

    if not documents:
        return {
            "answer": "No relevant documents found.",
            "sources": []
        }

    context = "\n\n".join(documents)

    prompt = f"""
You are an enterprise AI assistant.

Use the context below to answer the question.
If the context is partially relevant, summarize the relevant information.
If the exact answer is not present, explain what related information was found.
Do not invent information outside the context."

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

    sources = []

    for metadata, distance in zip(metadatas, distances):

        if metadata is None:
            metadata = {}

        sources.append({
            "source": metadata.get("source", "unknown"),
            "page": metadata.get("page", None),
            "chunk": metadata.get("chunk", None),
            "distance": distance
        })

    return {
        "answer": answer,
        "sources": sources
    }

def reset_knowledge_base():

    global collection

    chroma_client.delete_collection(
        name="documents"
    )

    collection = chroma_client.get_or_create_collection(
        name="documents"
    )

    ingest_result = ingest_documents()

    return {
        "message": "Knowledge base reset successfully",
        "ingest_result": ingest_result
    }
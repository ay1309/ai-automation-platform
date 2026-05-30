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



DOCUMENTS_PATH = os.getenv(
    "DOCUMENTS_PATH",
    "/app/documents"
)

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "/app/chroma_db"
)

COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "talent_documents"
)


# Ensure folders exist
os.makedirs(DOCUMENTS_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)


# ChromaDB persistent client
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# Text splitter
# Good for resumes, job descriptions, policies, and hiring guides.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300
)


def ingest_documents():

    pdf_files = glob.glob(
        f"{DOCUMENTS_PATH}/*.pdf"
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

            if not page_text or not page_text.strip():
                continue

            chunks = text_splitter.split_text(page_text)

            for chunk in chunks:

                if not chunk.strip():
                    continue

                filename = os.path.basename(pdf_file)

                all_chunks.append(chunk)

                all_metadatas.append({
                    "source": filename,
                    "page": page_number,
                    "chunk": counter,
                    "document_type": "talent_document"
                })

                safe_filename = filename.replace(" ", "_")

                all_ids.append(
                    f"{safe_filename}_page_{page_number}_chunk_{counter}"
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
        "message": "Talent documents ingested successfully",
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
            "answer": "No relevant talent acquisition documents were found for this question.",
            "sources": []
        }

    context_blocks = []

    for index, document in enumerate(documents):
        metadata = metadatas[index] or {}

        source = metadata.get("source", "unknown")
        page = metadata.get("page", "N/A")
        chunk = metadata.get("chunk", "N/A")

        context_blocks.append(
            f"""
[Source: {source} | Page: {page} | Chunk: {chunk}]
{document}
"""
        )

    context = "\n\n".join(context_blocks)

    system_prompt = """
You are AFMB Talent Assistant, an AI assistant specialized in talent acquisition, recruiting operations, candidate screening, and hiring documentation.

Your role is to help recruiters and hiring teams understand information contained in uploaded documents such as resumes, job descriptions, interview guides, hiring policies, recruiting playbooks, and internal talent acquisition documents.

Rules:
1. Answer only using the retrieved document context.
2. Do not invent candidate information, job requirements, dates, companies, skills, scores, or hiring decisions.
3. If the context is partially relevant, summarize the relevant information and clearly state what is missing.
4. If the answer is not available in the context, say that the information was not found in the uploaded documents.
5. When discussing candidates, use neutral and professional language.
6. Do not make discriminatory, sensitive, or protected-class judgments.
7. Do not infer age, gender, ethnicity, religion, disability, family status, or other protected attributes.
8. If asked to compare candidates, compare only job-relevant qualifications explicitly present in the documents.
9. If asked for a recommendation, frame it as evidence-based support, not a final hiring decision.
10. Prefer concise, structured answers with bullet points when useful.
"""

    user_prompt = f"""
Retrieved document context:
{context}

Recruiter question:
{question}

Answer as a professional talent acquisition assistant.
Include only information supported by the retrieved context.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.2
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

    try:
        chroma_client.delete_collection( 
            name=COLLECTION_NAME
        )
    except Exception:
        pass

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    ingest_result = ingest_documents()

    return {
        "message": "Talent knowledge base reset",
        "ingest_result": ingest_result
    }
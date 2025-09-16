#!/usr/bin/env python3
import os
import sys
import uuid
import re
from typing import List
from urllib.parse import urlparse

import requests
import pdfplumber
import chromadb

CHROMA_HOST = os.environ.get("CHROMA_HOST", "http://localhost:8000")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
TIMEOUT = 30


def embed(texts: List[str]) -> List[List[float]]:
    vectors = []
    for text in texts:
        try:
            r = requests.post(
                f"{OLLAMA_HOST}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": text},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()
            vectors.append(data["embedding"])
        except Exception as e:
            raise RuntimeError(f"Embedding failed: {e}") from e
    return vectors


def load_pdf(path: str) -> List[str]:
    paragraphs: List[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for para in re.split(r"\n\s*\n", text):
                p = para.strip()
                if p:
                    paragraphs.append(p)
    # chunk paragraphs into groups of max 800 tokens
    chunks: List[str] = []
    current: List[str] = []
    token_count = 0
    for para in paragraphs:
        tokens = para.split()
        if token_count + len(tokens) > 800 and current:
            chunks.append("\n\n".join(current))
            current = [para]
            token_count = len(tokens)
        else:
            current.append(para)
            token_count += len(tokens)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python embed_to_chroma.py <pdf_path>")
        return 1
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return 1
    try:
        texts = load_pdf(path)
        if not texts:
            print("No text found in document")
            return 1
        vectors = embed(texts)
        url = urlparse(CHROMA_HOST)
        client = chromadb.HttpClient(host=url.hostname, port=url.port)
        collection = client.get_or_create_collection("auditdocs")
        ids = [str(uuid.uuid4()) for _ in texts]
        metadatas = [{"source": path, "chunk_idx": i} for i, _ in enumerate(texts)]
        collection.add(
            ids=ids, metadatas=metadatas, documents=texts, embeddings=vectors
        )
        print(f"Inserted {len(texts)} chunks into 'auditdocs'")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
import os
import sys
from typing import List
from urllib.parse import urlparse

import requests
import chromadb

CHROMA_HOST = os.environ.get("CHROMA_HOST", "http://localhost:8000")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "llama3")
TIMEOUT = 30


def embed(text: str) -> List[float]:
    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()["embedding"]
    except Exception as e:
        raise RuntimeError(f"Embedding failed: {e}") from e


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python query_chroma.py "QUESTION"')
        return 1
    question = sys.argv[1]
    try:
        url = urlparse(CHROMA_HOST)
        client = chromadb.HttpClient(host=url.hostname, port=url.port)
        collection = client.get_collection("auditdocs")
        q_emb = embed(question)
        results = collection.query(
            query_embeddings=[q_emb], n_results=5, include=["documents", "ids"]
        )
        docs = results["documents"][0]
        ids = results["ids"][0]
        context = "\n".join(f"[{i}] {d}" for i, d in zip(ids, docs))
        prompt = (
            f"{context}\n\nAnswer the question based on the above documents.\n"
            f"Question: {question}"
        )
        r = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": CHAT_MODEL,
                "prompt": prompt,
                "system": "You are a helpful assistant.",
                "stream": False,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        answer = r.json().get("response", "").strip()
        print(answer)
        print("Sources:", ", ".join(ids))
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

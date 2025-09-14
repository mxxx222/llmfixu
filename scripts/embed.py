#!/usr/bin/env python3
"""
Minimaalinen embed-skripti ChromaDB:lle
"""
import requests
import json

def embed_text(text, collection_name="documents"):
    """Tallenna teksti ChromaDB:hen"""
    url = "http://localhost:8000/api/v1/collections"
    
    # Luo kokoelma
    collection_data = {
        "name": collection_name,
        "metadata": {"description": "Dokumenttikokoelma"}
    }
    
    try:
        response = requests.post(url, json=collection_data)
        print(f"Kokoelma luotu: {response.status_code}")
    except:
        print("Kokoelma on jo olemassa tai virhe")
    
    # Lisää dokumentti
    add_url = f"http://localhost:8000/api/v1/collections/{collection_name}/add"
    doc_data = {
        "documents": [text],
        "ids": [f"doc_{hash(text)}"],
        "metadatas": [{"source": "manual"}]
    }
    
    response = requests.post(add_url, json=doc_data)
    print(f"Dokumentti tallennettu: {response.status_code}")

if __name__ == "__main__":
    text = input("Anna teksti tallennettavaksi: ")
    embed_text(text)
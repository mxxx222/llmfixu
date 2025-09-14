#!/usr/bin/env python3
"""
Kehittynyt diagnostiikkaskripti palveluiden testaamiseen
"""
import requests
import time
import sys
import os

def check_service(name, url, expected_status=200):
    """Tarkista palvelun tila"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {name}: OK (status {response.status_code})")
            return True
        else:
            print(f"⚠️ {name}: Odottamaton status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Ei saavutettavissa ({e})")
        return False

def test_embedding():
    """Testaa embedding-toiminnallisuus"""
    print("\n=== Testaa embedding ===")
    
    # Luo testikokoelma
    try:
        collection_url = "http://localhost:8000/api/v1/collections"
        collection_data = {
            "name": "test_collection",
            "metadata": {"description": "Testikokoelma"}
        }
        
        response = requests.post(collection_url, json=collection_data)
        print(f"Testikokoelma: {response.status_code}")
        
        # Lisää testidokumentti
        add_url = "http://localhost:8000/api/v1/collections/test_collection/add"
        doc_data = {
            "documents": ["Tämä on testidokumentti AI-auditointijärjestelmälle."],
            "ids": ["test_doc_1"],
            "metadatas": [{"source": "diagnostic_test"}]
        }
        
        response = requests.post(add_url, json=doc_data)
        if response.status_code == 200:
            print("✅ Dokumentin lisäys onnistui")
        else:
            print(f"❌ Dokumentin lisäys epäonnistui: {response.status_code}")
            
        # Testaa haku
        query_url = "http://localhost:8000/api/v1/collections/test_collection/query"
        query_data = {
            "query_texts": ["testidokumentti"],
            "n_results": 1
        }
        
        response = requests.post(query_url, json=query_data)
        if response.status_code == 200:
            results = response.json()
            if results.get('documents') and len(results['documents'][0]) > 0:
                print("✅ Dokumenttihaku onnistui")
            else:
                print("⚠️ Dokumenttihaku palautti tyhjän tuloksen")
        else:
            print(f"❌ Dokumenttihaku epäonnistui: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Embedding-testi epäonnistui: {e}")

def main():
    print("=== LLMFixU Diagnostiikka ===\n")
    
    services = [
        ("Ollama API", "http://localhost:11434/api/tags"),
        ("ChromaDB", "http://localhost:8000/api/v1/heartbeat"),
        ("OpenWebUI", "http://localhost:3000"),
        ("n8n", "http://localhost:5678")
    ]
    
    print("=== Palveluiden tila ===")
    all_ok = True
    for name, url in services:
        if not check_service(name, url):
            all_ok = False
    
    if all_ok:
        print("\n✅ Kaikki peruspalvelut toimivat!")
        test_embedding()
    else:
        print("\n❌ Jotkin palvelut eivät vastaa. Tarkista 'docker-compose logs'")
        sys.exit(1)
    
    print("\n=== Käyttöohjeet ===")
    print("Palvelut käytettävissä:")
    print("- OpenWebUI: http://localhost:3000")
    print("- n8n: http://localhost:5678") 
    print("- ChromaDB API: http://localhost:8000")
    print("- Ollama API: http://localhost:11434")

if __name__ == "__main__":
    main()
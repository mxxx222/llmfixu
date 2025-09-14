#!/usr/bin/env python3
"""
Minimaalinen query-skripti ChromaDB:lle
"""
import requests
import json

def query_documents(query, collection_name="documents", n_results=3):
    """Hae dokumentteja ChromaDB:stä"""
    url = f"http://localhost:8000/api/v1/collections/{collection_name}/query"
    
    query_data = {
        "query_texts": [query],
        "n_results": n_results
    }
    
    try:
        response = requests.post(url, json=query_data)
        if response.status_code == 200:
            results = response.json()
            print(f"Löytyi {len(results.get('documents', [[]])[0])} dokumenttia:")
            
            for i, doc in enumerate(results.get('documents', [[]])[0]):
                distance = results.get('distances', [[]])[0][i] if results.get('distances') else 'N/A'
                print(f"\n{i+1}. Etäisyys: {distance}")
                print(f"Sisältö: {doc[:200]}...")
        else:
            print(f"Virhe haussa: {response.status_code}")
    except Exception as e:
        print(f"Virhe: {e}")

if __name__ == "__main__":
    query = input("Anna hakukysely: ")
    query_documents(query)
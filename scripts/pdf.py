#!/usr/bin/env python3
"""
Minimaalinen PDF-käsittelyskripti
"""
import requests
import json
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def process_pdf(pdf_path, collection_name="documents"):
    """Käsittele PDF ja tallenna ChromaDB:hen"""
    if not PDF_AVAILABLE:
        print("PyPDF2 ei ole asennettu. Asenna: pip install PyPDF2")
        return
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        # Jaa teksti kappaleisiin
        chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
        
        # Tallenna ChromaDB:hen
        url = f"http://localhost:8000/api/v1/collections/{collection_name}/add"
        
        for i, chunk in enumerate(chunks):
            if len(chunk) > 50:  # Ohita liian lyhyet kappaleet
                doc_data = {
                    "documents": [chunk],
                    "ids": [f"pdf_{pdf_path}_{i}"],
                    "metadatas": [{"source": pdf_path, "chunk": i}]
                }
                
                response = requests.post(url, json=doc_data)
                print(f"Kappale {i+1} tallennettu: {response.status_code}")
        
        print(f"PDF käsitelty: {len(chunks)} kappaletta")
        
    except Exception as e:
        print(f"Virhe PDF:n käsittelyssä: {e}")

if __name__ == "__main__":
    pdf_path = input("Anna PDF-tiedoston polku: ")
    process_pdf(pdf_path)
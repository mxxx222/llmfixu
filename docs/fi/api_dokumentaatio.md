# LLMFixU API-dokumentaatio

## Yleiskatsaus

LLMFixU tarjoaa Python API:n dokumenttien käsittelyyn ja kyselyihin. Tämä dokumentaatio kertoo kuinka API:a käytetään ohjelmallisesti.

## Pääluokat

### QueryEngine

Pääluokka kyselyiden tekemiseen.

```python
from src.llmfixu.api.query_engine import QueryEngine

engine = QueryEngine()
```

#### Metodit

##### `query(question, n_context_docs=3, model=None, **kwargs)`

Tekee kyselyn RAG-menetelmällä (Retrieval-Augmented Generation).

**Parametrit:**
- `question` (str): Kysymys
- `n_context_docs` (int): Kontekstidokumenttien määrä (oletus: 3)
- `model` (str): LLM-malli (oletus: konfiguraatiosta)
- `**kwargs`: Lisäparametrit

**Palauttaa:**
```python
{
    'answer': str,           # Generoitu vastaus
    'sources': [             # Lähdedokumentit
        {
            'id': str,
            'file_name': str,
            'file_path': str,
            'relevance_score': float
        }
    ],
    'context_docs': [        # Kontekstidokumentit
        {
            'id': str,
            'content': str,
            'metadata': dict,
            'distance': float
        }
    ],
    'confidence': float,     # Luotettavuus 0-1
    'model_used': str        # Käytetty malli
}
```

**Esimerkki:**
```python
result = engine.query("Mitä turvallisuusvaatimuksia on?")
print(result['answer'])
print(f"Luotettavuus: {result['confidence']:.2%}")
```

##### `batch_query(questions, **kwargs)`

Käsittelee useita kyselyitä kerralla.

**Parametrit:**
- `questions` (List[str]): Lista kysymyksiä
- `**kwargs`: Lisäparametrit jokaiselle kyselylle

**Esimerkki:**
```python
questions = [
    "Mitkä ovat pääriskit?",
    "Kuka on vastuussa turvallisuudesta?",
    "Milloin seuraava auditointi?"
]

results = engine.batch_query(questions)
for i, result in enumerate(results):
    print(f"Q{i+1}: {questions[i]}")
    print(f"A{i+1}: {result['answer']}\n")
```

##### `get_similar_documents(query, n_results=10)`

Hakee samankaltaisia dokumentteja ilman LLM-generointia.

**Esimerkki:**
```python
docs = engine.get_similar_documents("turvallisuus", n_results=5)
for doc in docs:
    print(f"Tiedosto: {doc['metadata']['file_name']}")
    print(f"Sisältö: {doc['content'][:100]}...")
```

##### `health_check()`

Tarkistaa järjestelmän tilan.

**Palauttaa:**
```python
{
    'vector_database': bool,
    'ollama_service': bool,
    'overall': bool
}
```

### DocumentProcessor

Dokumenttien käsittely ja tekstitietojen erottaminen.

```python
from src.llmfixu.processors.document_processor import DocumentProcessor

processor = DocumentProcessor()
```

#### Metodit

##### `process_file(file_path)`

Käsittelee yksittäisen tiedoston.

**Palauttaa:**
```python
{
    'file_path': str,
    'file_name': str,
    'file_size': int,
    'file_hash': str,
    'file_type': str,
    'content': str,
    'content_length': int
}
```

**Esimerkki:**
```python
metadata = processor.process_file("/polku/dokumentti.pdf")
if metadata:
    print(f"Käsitelty: {metadata['file_name']}")
    print(f"Koko: {metadata['file_size']} tavua")
    print(f"Sisältö: {metadata['content'][:200]}...")
```

##### `chunk_content(content, chunk_size=None, overlap=None)`

Jakaa tekstin osiin vektorointia varten.

**Esimerkki:**
```python
chunks = processor.chunk_content(
    content="Pitkä teksti...", 
    chunk_size=1000, 
    overlap=200
)
print(f"Luotiin {len(chunks)} osiota")
```

### VectorManager

Vektorietietokannan hallinta ChromaDB:llä.

```python
from src.llmfixu.processors.vector_manager import VectorManager

vector_manager = VectorManager()
```

#### Metodit

##### `add_documents(documents)`

Lisää dokumentteja vektorietietokantaan.

**Esimerkki:**
```python
documents = [
    {
        'content': "Dokumentin sisältö...",
        'metadata': {
            'file_name': 'esimerkki.pdf',
            'file_path': '/polku/esimerkki.pdf'
        }
    }
]

success = vector_manager.add_documents(documents)
if success:
    print("Dokumentit lisätty onnistuneesti")
```

##### `search_documents(query, n_results=5, where=None)`

Hakee samankaltaisia dokumentteja.

**Esimerkki:**
```python
# Perusshaku
results = vector_manager.search_documents("turvallisuus")

# Metadata-suodatin
results = vector_manager.search_documents(
    query="auditointi",
    n_results=10,
    where={"file_type": "pdf"}
)
```

##### `get_collection_info()`

Palauttaa kokoelman tiedot.

##### `clear_collection()`

Tyhjentää kokoelman.

### OllamaClient

LLM-palvelun asiakasohjelma.

```python
from src.llmfixu.api.ollama_client import OllamaClient

ollama = OllamaClient()
```

#### Metodit

##### `generate_response(prompt, model=None, context=None, **kwargs)`

Generoi vastauksen LLM:llä.

**Esimerkki:**
```python
response = ollama.generate_response(
    prompt="Selitä tekoälyn perusteet",
    model="llama2",
    temperature=0.7
)
print(response)
```

##### `list_models()`

Listaa saatavilla olevat mallit.

##### `is_available()`

Tarkistaa palvelun saatavuuden.

## Konfiguraatio

### Config-luokka

```python
from src.llmfixu.config.settings import config

# Palveluiden URL:t
print(config.OLLAMA_URL)
print(config.CHROMADB_URL)

# AI-asetukset
print(config.DEFAULT_MODEL)
print(config.TEMPERATURE)

# Dokumenttiasetukset
print(config.CHUNK_SIZE)
print(config.SUPPORTED_FORMATS)
```

### Ympäristömuuttujat

Konfiguraatio ladataan automaattisesti ympäristömuuttujista:

```bash
export OLLAMA_URL="http://localhost:11434"
export DEFAULT_MODEL="llama2:13b"
export CHUNK_SIZE="1500"
```

## Apuvälineet

### Helpers-moduuli

```python
from src.llmfixu.utils.helpers import (
    setup_logging,
    find_files,
    validate_environment,
    format_file_size
)

# Lokien asetus
setup_logging(log_level="DEBUG")

# Tiedostojen haku
files = find_files("/polku/hakemistoon", ["pdf", "docx"])

# Ympäristön validointi
env_ok = validate_environment()
print(f"Ympäristö kunnossa: {all(env_ok.values())}")

# Tiedostokoon muotoilu
size_str = format_file_size(1024000)  # "1.0 MB"
```

## Käytännön esimerkkejä

### Peruskyselyohjelma

```python
#!/usr/bin/env python3
"""
Yksinkertainen kyselyohjelma.
"""

import sys
from src.llmfixu.api.query_engine import QueryEngine
from src.llmfixu.utils.helpers import setup_logging

def main():
    setup_logging()
    
    engine = QueryEngine()
    
    # Tarkista tila
    health = engine.health_check()
    if not health['overall']:
        print("Järjestelmä ei ole käytettävissä")
        return 1
    
    # Kysy käyttäjältä
    question = input("Kysymys: ")
    
    # Tee kysely
    result = engine.query(question)
    
    # Tulosta vastaus
    print(f"\nVastaus: {result['answer']}")
    print(f"Luotettavuus: {result['confidence']:.1%}")
    
    if result['sources']:
        print("\nLähteet:")
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['file_name']}")

if __name__ == '__main__':
    sys.exit(main())
```

### Batch-prosessointiohjelma

```python
#!/usr/bin/env python3
"""
Käsittelee useita kyselyitä CSV-tiedostosta.
"""

import csv
import sys
from src.llmfixu.api.query_engine import QueryEngine

def process_questions_from_csv(csv_file, output_file):
    engine = QueryEngine()
    
    questions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        questions = [row[0] for row in reader if row]
    
    print(f"Käsitellään {len(questions)} kysymystä...")
    
    results = engine.batch_query(questions)
    
    # Kirjoita tulokset
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Kysymys', 'Vastaus', 'Luotettavuus', 'Lähteet'])
        
        for q, r in zip(questions, results):
            sources = '; '.join([s['file_name'] for s in r['sources']])
            writer.writerow([
                q,
                r['answer'],
                f"{r['confidence']:.1%}",
                sources
            ])
    
    print(f"Tulokset tallennettu: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Käyttö: python script.py kysymykset.csv tulokset.csv")
        sys.exit(1)
    
    process_questions_from_csv(sys.argv[1], sys.argv[2])
```

### Dokumenttien automaattinen käsittely

```python
#!/usr/bin/env python3
"""
Valvoo hakemistoa ja käsittelee uudet dokumentit automaattisesti.
"""

import time
import os
from pathlib import Path
from src.llmfixu.processors.document_processor import DocumentProcessor
from src.llmfixu.processors.vector_manager import VectorManager

def watch_directory(watch_dir, interval=60):
    processor = DocumentProcessor()
    vector_manager = VectorManager()
    
    processed_files = set()
    
    print(f"Valvotaan hakemistoa: {watch_dir}")
    
    while True:
        try:
            # Etsi uudet tiedostot
            for file_path in Path(watch_dir).rglob('*'):
                if (file_path.is_file() and 
                    file_path.suffix.lower().lstrip('.') in processor.supported_formats and
                    str(file_path) not in processed_files):
                    
                    print(f"Uusi tiedosto: {file_path}")
                    
                    # Käsittele tiedosto
                    metadata = processor.process_file(str(file_path))
                    if metadata:
                        # Jaa osiin
                        chunks = processor.chunk_content(metadata['content'])
                        
                        # Lisää vektorietietokantaan
                        documents = [{
                            'content': chunk,
                            'metadata': {
                                'file_name': metadata['file_name'],
                                'file_path': metadata['file_path'],
                                'file_type': metadata['file_type'],
                                'chunk_index': i,
                                'total_chunks': len(chunks)
                            }
                        } for i, chunk in enumerate(chunks)]
                        
                        if vector_manager.add_documents(documents):
                            print(f"Käsitelty: {file_path} ({len(chunks)} osiota)")
                            processed_files.add(str(file_path))
                        else:
                            print(f"Virhe käsittelyssä: {file_path}")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("Valvonta pysäytetty")
            break
        except Exception as e:
            print(f"Virhe: {e}")
            time.sleep(interval)

if __name__ == '__main__':
    watch_directory("data/documents/", interval=30)
```

## Virheenkäsittely

### Yleisiä virheitä

```python
from src.llmfixu.api.query_engine import QueryEngine

engine = QueryEngine()

try:
    result = engine.query("Kysymys")
except Exception as e:
    if "Ollama" in str(e):
        print("LLM-palvelu ei ole käytettävissä")
    elif "Chroma" in str(e):
        print("Vektorietietokanta ei ole käytettävissä")
    else:
        print(f"Tuntematon virhe: {e}")
```

### Timeout-käsittely

```python
import requests
from src.llmfixu.api.ollama_client import OllamaClient

ollama = OllamaClient()

try:
    response = ollama.generate_response(
        "Pitkä kysymys...",
        timeout=120  # 2 minuuttia
    )
except requests.exceptions.Timeout:
    print("Kysely aikakatkaistiin")
except requests.exceptions.ConnectionError:
    print("Yhteysvirhe Ollama-palveluun")
```

## Testaus

### Yksikkötestit

```python
import unittest
from src.llmfixu.processors.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = DocumentProcessor()
    
    def test_chunk_content(self):
        content = "A" * 2000
        chunks = self.processor.chunk_content(content, chunk_size=500, overlap=100)
        
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), 500)
    
    def test_supported_formats(self):
        self.assertIn('pdf', self.processor.supported_formats)
        self.assertIn('docx', self.processor.supported_formats)

if __name__ == '__main__':
    unittest.main()
```

### Integraatiotestit

```python
def test_full_pipeline():
    from src.llmfixu.processors.document_processor import DocumentProcessor
    from src.llmfixu.processors.vector_manager import VectorManager
    from src.llmfixu.api.query_engine import QueryEngine
    
    # Luo testimateriaali
    test_content = "Testiorganisaatio noudattaa tiukkoja turvallisuusvaatimuksia."
    
    # Käsittele
    processor = DocumentProcessor()
    chunks = processor.chunk_content(test_content)
    
    # Lisää vektorietietokantaan
    vector_manager = VectorManager()
    documents = [{
        'content': chunk,
        'metadata': {'test': True}
    } for chunk in chunks]
    
    assert vector_manager.add_documents(documents)
    
    # Tee kysely
    engine = QueryEngine()
    result = engine.query("Millaisia turvallisuusvaatimuksia on?")
    
    assert result['answer']
    assert result['confidence'] > 0
    
    print("Integraatiotesti onnistui!")

if __name__ == '__main__':
    test_full_pipeline()
```

## Lisätietoja

- [Käyttöohje](kayttoohje.md)
- [Vianmääritys](vianmaaritys.md) 
- [Kehittäjän opas](kehittajan_opas.md)
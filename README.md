# Auditointi-AI

Tekoälyavusteinen auditointijärjestelmä, joka hyödyntää moderneja LLM-työkaluja dokumenttien analysointiin ja tiedon hakuun.

## Järjestelmän komponentit

**Docker-compose sisältää:**
- **Ollama** - Paikallinen LLM-palvelin
- **OpenWebUI** - Käyttöliittymä chat-vuorovaikutukseen
- **Chroma** - Vektoritietokanta embeddingeille
- **n8n** - Työnkulkujen automatisointi

## Pika-aloitus

```bash
# 1. Käynnistä palvelut
docker-compose up -d

# 2. Lataa malli Ollamaan
docker exec -it ollama ollama pull llama2

# 3. Käyttöliittymät
# OpenWebUI: http://localhost:3000
# n8n: http://localhost:5678
# Chroma: http://localhost:8000
```

## Minimiskriptit

### Embedding-skripti
```python
# embed.py - Luo embeddingjä dokumenteista
import chromadb
client = chromadb.Client()
collection = client.create_collection("documents")
# Lisää dokumentit kokoelmaan
```

### Haku-skripti
```python
# query.py - Hae samankaltaisia dokumentteja
results = collection.query(
    query_texts=["hakusana"],
    n_results=5
)
```

### PDF-käsittely
```python
# pdf.py - Käsittele PDF-tiedostoja
import PyPDF2
# Lue PDF, jaa osiin, luo embeddingjä
```

## n8n-työnkulku

**Automaattinen dokumenttien käsittely:**
1. **URL-syöte** → Verkko-osoitteen vastaanotto
2. **Crawl** → Sivuston sisällön haku
3. **Embed** → Tekstin muunto vektoreiksi
4. **Chroma** → Tallennus tietokantaan

Työnkulku mahdollistaa automaattisen auditointiaineiston keräämisen ja analysoinnin.
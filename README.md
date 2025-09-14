# llmfixu

## Setup

Start services:

```
docker compose up -d
```

Pull embedding model:

```
ollama pull nomic-embed-text
```

Install dependencies:

```
pip install chromadb pdfplumber requests
```

Check services:

```
curl $CHROMA_HOST/api/v1/heartbeat
curl $OLLAMA_HOST/api/tags
```

## Usage

Embed a PDF:

```
python embed_to_chroma.py docs/example.pdf
```

Ask a question:

```
python query_chroma.py "Mikä on dokumentin pääpointti?"
```

Open WebUI runs at [http://localhost:3000](http://localhost:3000).


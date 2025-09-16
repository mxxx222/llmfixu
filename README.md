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

Quick diagnostics:

```
make diag
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

Open WebUI runs at [http://localhost:${OPENWEBUI_PORT:-8080}](http://localhost:8080) and n8n is available at [http://localhost:5678](http://localhost:5678).

## Troubleshooting

If services do not respond or ports appear closed, try the following steps:

1. **Check container state**

   ```bash
   docker compose ps
   docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
   ```

2. **Start missing services and inspect logs**

   ```bash
   docker compose up -d
   docker compose logs -f openwebui
   docker compose logs -f ollama
   docker compose logs -f chroma
   docker compose logs -f n8n
   ```

3. **Verify ports on the host**

   ```bash
   lsof -iTCP:8080 -sTCP:LISTEN
   lsof -iTCP:11434 -sTCP:LISTEN
   lsof -iTCP:8000 -sTCP:LISTEN
   lsof -iTCP:5678 -sTCP:LISTEN
   ```

4. **Test services via curl**

   ```bash
   curl -I http://127.0.0.1:8080
   curl http://127.0.0.1:11434/api/tags
   curl http://127.0.0.1:8000/api/v1/heartbeat
   curl -I http://127.0.0.1:5678
   ```

5. **Try 127.0.0.1 instead of localhost and a different browser**

   * http://127.0.0.1:8080 (Open WebUI)
   * http://127.0.0.1:5678 (n8n)

6. **General fixes**

   * Temporarily disable VPNs or firewalls.
   * Ensure `.env` is in the project root with `docker-compose.yml`.
   * Confirm port mappings in `docker-compose.yml`:
     * `11434:11434` (ollama)
     * `8000:8000` (chroma)
     * `${OPENWEBUI_PORT:-8080}:8080` (openwebui)
     * `5678:5678` (n8n)

7. **Quick diagnostics**

   ```bash
   make diag
   ```

If Open WebUI logs contain `cannot reach Ollama`, set Connections → Ollama URL to `http://ollama:11434` and restart the service:

```bash
docker compose restart openwebui
```

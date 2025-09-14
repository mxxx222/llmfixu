# LLMFixU - Auditointi-AI järjestelmä

Kattava AI-pohjainen auditointijärjestelmä Docker-compose -ratkaisulla. Sisältää Ollama LLM:n, OpenWebUI:n, ChromaDB vektoritietokannan ja n8n automaation.

## ⚡ Pikakynnistys (1 komento)

```bash
./setup.sh
```

Tämä skripti:
- Asentaa Python-riippuvuudet
- Käynnistää kaikki Docker-palvelut
- Lataa perusmallin Ollamaan
- Suorittaa diagnostiikan
- Antaa käyttöohjeet

## 🚀 Pikakäynnistys

### 1. Käynnistä palvelut
```bash
docker compose up -d
```

### 2. Lataa malli Ollamaan
```bash
docker exec ollama ollama pull llama2:7b
# Tai suomenkieliseen malliin:
docker exec ollama ollama pull orca-mini:3b
```

### 3. Käyttöliittymät
- **OpenWebUI**: http://localhost:3000 (Chat-käyttöliittymä)
- **ChromaDB**: http://localhost:8000 (Vektoritietokanta API)
- **n8n**: http://localhost:5678 (Workflow-automaatio)
- **Ollama**: http://localhost:11434 (LLM API)

## 📝 Minimiskriptit

### Dokumenttien tallennus (embed.py)
```bash
python scripts/embed.py
# Syötä teksti -> tallentuu ChromaDB:hen
```

### Dokumenttien haku (query.py)
```bash
python scripts/query.py
# Syötä hakukysely -> löytää samankaltaiset dokumentit
```

### PDF-käsittely (pdf.py)
```bash
pip install PyPDF2
python scripts/pdf.py
# Syötä PDF-polku -> pilkkoo ja tallentaa ChromaDB:hen
```

## 🔄 n8n Workflow: URL→Crawl→Embed→Chroma

### Workflow-rakenne:
1. **HTTP Trigger** - Vastaanottaa URL:n
2. **HTTP Request** - Hakee web-sivun sisällön
3. **HTML Extract** - Purkaa tekstin HTML:stä
4. **Text Splitter** - Pilkkoo tekstin kappaleiksi
5. **ChromaDB Node** - Tallentaa embedaukset

### Käyttöönotto n8n:ssä:
1. Avaa http://localhost:5678
2. Luo uusi workflow
3. Lisää HTTP Trigger node (webhook)
4. Konfiguroi HTTP Request node hakemaan `{{$json.url}}`
5. Lisää HTML Extract node tekstin purkamiseen
6. Yhdistä ChromaDB node (endpoint: http://chroma:8000)
7. Aktivoi workflow

### Testaus:
```bash
curl -X POST http://localhost:5678/webhook/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## 🛠️ Diagnostiikka

### Tarkista palveluiden tila
```bash
make diag
```

### Asenna riippuvuudet
```bash
pip install requests PyPDF2
```

## 💡 Käyttötapaukset
- **Dokumenttien auditointi**: Lataa PDF:t ja hae epäjohdonmukaisuuksia
- **Web-sisällön seuranta**: Automaattinen crawling ja muutosten tunnistus  
- **Tietämyshallinta**: Keskitetty dokumenttihaku ja -analyysi
- **Compliance-tarkistus**: Sääntöjen vastaavuuden automaattinen arviointi

## 🛠️ Vaatimukset
- Docker & Docker Compose
- Python 3.8+ (skripteihin)
- 8GB RAM (suositus)

Järjestelmä on valmis käyttöön muutamassa minuutissa!
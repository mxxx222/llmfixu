# LLMFixU - Tekoälyavusteinen Dokumenttianalyysi ja Auditointijärjestelmä

## Yleiskuvaus

LLMFixU on kokonaisvaltainen tekoälyavusteinen järjestelmä dokumenttien analysointiin, kyselyihin ja auditointiin. Järjestelmä hyödyntää:

- **Ollama** - Paikallinen LLM-palvelin
- **OpenWebUI** - Käyttöliittymä LLM-vuorovaikutukseen
- **ChromaDB** - Vektorietietokannat semanttiseen hakuun
- **n8n** - Automaatiotyökalut prosessien hallintaan

## Toiminnallisuudet

- 📄 **Dokumenttien käsittely**: PDF, DOCX, TXT, MD, HTML tiedostot
- 🔍 **Semanttinen haku**: Älykkäs dokumenttihaku vektorietokannasta
- 🤖 **LLM-integraatio**: Suomenkieliset vastaukset dokumenttien pohjalta
- 🐳 **Docker Compose**: Helppo käyttöönotto konttiteknologialla
- 🛠️ **Diagnostiikkatyökalut**: Järjestelmän tilan valvonta
- 📊 **API**: Python-rajapinta integraatioille

## Projektin rakenne

```
llmfixu/
├── docker-compose.yml          # Docker-palveluiden määritykset
├── .env.example               # Ympäristömuuttujien malli
├── requirements.txt           # Python-riippuvuudet
├── src/llmfixu/              # Pääsovelluksen koodi
│   ├── processors/           # Dokumenttien käsittely
│   ├── api/                  # API ja LLM-asiakkaat
│   ├── config/               # Konfiguraatio
│   └── utils/                # Apuvälineet
├── scripts/                  # Komentorivin työkalut
├── docs/fi/                  # Suomenkielinen dokumentaatio
├── tests/                    # Testit
├── data/                     # Tiedot ja tietokannat
└── logs/                     # Lokitiedostot
```

## Pika-aloitus

### 1. Kloonaa repositorio

```bash
git clone https://github.com/mxxx222/llmfixu.git
cd llmfixu
```

### 2. Kopioi ympäristömääritykset

```bash
cp .env.example .env
# Muokkaa .env-tiedostoa tarpeen mukaan
```

### 3. Käynnistä palvelut

```bash
docker-compose up -d
```

### 4. Asenna Python-riippuvuudet

```bash
pip install -r requirements.txt
```

### 5. Lataa LLM-malli

```bash
docker exec llmfixu-ollama ollama pull llama2
```

### 6. Testaa järjestelmä

```bash
python scripts/diagnose_system.py
```

## Käyttöönotto

Katso yksityiskohtaiset ohjeet: [Asennusopas](docs/fi/asennusopas.md)

## Käyttö

### Dokumenttien syöttäminen

```bash
# Yksittäinen tiedosto
python scripts/ingest_documents.py /polku/dokumenttiin.pdf

# Koko hakemisto
python scripts/ingest_documents.py /polku/hakemistoon/ -r

# Tyhjennä tietokanta ensin
python scripts/ingest_documents.py /polku/hakemistoon/ --clear
```

### Kyselyiden tekeminen

```bash
# Yksittäinen kysymys
python scripts/query_system.py "Mitä tässä dokumentissa sanotaan turvallisuudesta?"

# Interaktiivinen tila
python scripts/query_system.py -i

# JSON-tuloste
python scripts/query_system.py "Kysymys" --json
```

### Järjestelmän diagnostiikka

```bash
python scripts/diagnose_system.py
```

## Palveluiden käyttöliittymät

Kun Docker Compose on käynnissä:

- **OpenWebUI**: http://localhost:3000 - LLM-käyttöliittymä
- **ChromaDB**: http://localhost:8000 - Vektorietietokanta
- **n8n**: http://localhost:5678 - Automaatiotyökalut (admin/changeme)
- **Ollama**: http://localhost:11434 - LLM API

## Kehittäjille

### Testien ajaminen

```bash
python -m pytest tests/
```

### Koodin formatointi

```bash
black src/ scripts/
flake8 src/ scripts/
```

## Lisätietoja

- [Käyttöohje](docs/fi/kayttoohje.md)
- [API-dokumentaatio](docs/fi/api_dokumentaatio.md)
- [Vianmääritys](docs/fi/vianmaaritys.md)
- [Kehittäjän opas](docs/fi/kehittajan_opas.md)

## Lisenssi

MIT License - katso LICENSE-tiedosto

## Tuki

Luo issue GitHubissa tai ota yhteyttä projektin ylläpitäjiin.
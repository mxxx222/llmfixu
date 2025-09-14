# LLMFixU Käyttöohje

## Yleiskatsaus

LLMFixU on tekoälyavusteinen dokumenttianalyysi- ja kyselyjärjestelmä. Tämä opas kertoo kuinka järjestelmää käytetään jokapäiväisessä työssä.

## Pääkomponentit

### 1. OpenWebUI (http://localhost:3000)
Graafinen käyttöliittymä LLM-vuorovaikutukseen.

### 2. Komentorivin työkalut
Python-skriptit dokumenttien hallintaan ja kyselyihin.

### 3. ChromaDB (http://localhost:8000)
Vektorietietokanta semanttista hakua varten.

### 4. n8n (http://localhost:5678)
Automaatiotyökalu prosessien hallintaan.

## Dokumenttien hallinta

### Tuetut tiedostomuodot

- **PDF**: `.pdf`
- **Microsoft Word**: `.docx`
- **Tekstitiedostot**: `.txt`
- **Markdown**: `.md`
- **HTML**: `.html`

### Dokumenttien syöttäminen

#### Yksittäinen tiedosto

```bash
python scripts/ingest_documents.py /polku/tiedostoon.pdf
```

#### Koko hakemisto

```bash
# Pelkästään hakemiston tiedostot
python scripts/ingest_documents.py /polku/hakemistoon/

# Rekursiivisesti kaikki alihakemistot
python scripts/ingest_documents.py /polku/hakemistoon/ --recursive
```

#### Lisäasetukset

```bash
# Tyhjennä tietokanta ennen syöttämistä
python scripts/ingest_documents.py /polku/ --clear

# Mukautettu chunk-koko
python scripts/ingest_documents.py /polku/ --chunk-size 1500 --chunk-overlap 300

# Yksityiskohtainen tuloste
python scripts/ingest_documents.py /polku/ --verbose
```

#### Esimerkki dokumenttien syöttämisestä

```bash
# Luo testihakemisto
mkdir -p data/documents/

# Kopioi dokumentteja hakemistoon
cp ~/Dokumentit/*.pdf data/documents/

# Syötä kaikki dokumentit
python scripts/ingest_documents.py data/documents/ --recursive --verbose
```

Odotettu tuloste:
```
🔍 Found 15 files to process
✅ Processing: data/documents/raportti1.pdf
✅ Successfully processed: data/documents/raportti1.pdf (12 chunks)
...
📊 INGESTION SUMMARY
Files processed: 15
Files failed: 0
Total size: 25.3 MB
Collection document count: 156
```

## Kyselyiden tekeminen

### Komentorivin käyttöliittymä

#### Yksittäinen kysymys

```bash
python scripts/query_system.py "Mitä dokumenteissa sanotaan tietoturvasta?"
```

#### Interaktiivinen tila

```bash
python scripts/query_system.py --interactive
```

Interaktiivisessa tilassa:
```
Kysymys: Mitä dokumenteissa sanotaan budjetista?
===============================================================
VASTAUS:
Dokumenttien mukaan budjetissa on varattu 500 000 euroa 
tietojärjestelmien kehittämiseen vuodelle 2024...

----------------------------------------
LÄHTEET:
1. taloussuunnitelma_2024.pdf (relevanssi: 89.3%)
2. budjetti_raportti.pdf (relevanssi: 76.8%)

Luotettavuus: 83.1%
```

#### Lisäasetukset

```bash
# Käytä tiettyä mallia
python scripts/query_system.py "Kysymys" --model llama2:13b

# Enemmän kontekstidokumentteja
python scripts/query_system.py "Kysymys" --context-docs 5

# JSON-tuloste ohjelmallista käyttöä varten
python scripts/query_system.py "Kysymys" --json

# Yksityiskohtainen tuloste
python scripts/query_system.py "Kysymys" --verbose
```

### Web-käyttöliittymä (OpenWebUI)

1. **Avaa selaimessa**: http://localhost:3000
2. **Rekisteröidy** tai **kirjaudu sisään**
3. **Valitse malli**: Esim. "llama2"
4. **Kirjoita kysymys** chat-kenttään
5. **Lähetä** painamalla Enter

**Huom**: Web-käyttöliittymässä dokumenttikonteksti ei ole automaattisesti käytössä. Käytä komentorivin työkaluja dokumenttipohjaisiin kyselyihin.

## Käytännön esimerkkejä

### Auditointikäyttö

```bash
# Syötä auditointiraportit
python scripts/ingest_documents.py /polku/auditointi_raportit/ --clear --recursive

# Analysoi turvallisuus
python scripts/query_system.py "Mitä turvallisuuspuutteita raporteissa on tunnistettu?"

# Tarkista compliance
python scripts/query_system.py "Onko järjestelmä GDPR-yhteensopiva?"

# Hae suositukset
python scripts/query_system.py "Mitä parannusehdotuksia raporteissa esitetään?"
```

### Sopimusanalyysi

```bash
# Syötä sopimukset
python scripts/ingest_documents.py /polku/sopimukset/ --recursive

# Analysoi vastuut
python scripts/query_system.py "Ketkä ovat vastuussa järjestelmän ylläpidosta?"

# Tarkista määräajat
python scripts/query_system.py "Milloin sopimukset päättyvät?"

# Hae taloudellinen tieto
python scripts/query_system.py "Paljonko sopimukset maksavat vuodessa?"
```

### Tekninen dokumentaatio

```bash
# Syötä tekniset dokumentit
python scripts/ingest_documents.py /polku/tekniset_dokumentit/ --recursive

# Hae API-tietoja
python scripts/query_system.py "Miten API-autentikointi toimii?"

# Tarkista arkkitehtuuri
python scripts/query_system.py "Millainen on järjestelmän arkkitehtuuri?"

# Ongelmanratkaisu
python scripts/query_system.py "Miten ratkaistaan tietokantayhteysongelmat?"
```

## Järjestelmän hallinta

### Tilan tarkistus

```bash
# Yleinen diagnostiikka
python scripts/diagnose_system.py

# JSON-muotoinen tila
python scripts/diagnose_system.py --json

# Yksityiskohtainen analyysi
python scripts/diagnose_system.py --verbose
```

### Palveluiden hallinta

```bash
# Tarkista Docker-palvelut
docker-compose ps

# Käynnistä palvelut
docker-compose up -d

# Pysäytä palvelut
docker-compose down

# Käynnistä uudelleen
docker-compose restart

# Katso lokeja
docker-compose logs ollama
docker-compose logs chromadb
```

### Tietokannan hallinta

```bash
# Tietokannan tyhjennys
python -c "
from src.llmfixu.processors.vector_manager import VectorManager
vm = VectorManager()
vm.clear_collection()
print('Tietokanta tyhjennetty')
"

# Tietokannan tilastot
python -c "
from src.llmfixu.processors.vector_manager import VectorManager
vm = VectorManager()
info = vm.get_collection_info()
print(f'Dokumentteja: {info.get(\"document_count\", 0)}')
"
```

## Vianmääritys

### Yleiset ongelmat

#### "Ei dokumentteja löytynyt"

1. Tarkista että dokumentit on syötetty:
   ```bash
   python scripts/diagnose_system.py
   ```

2. Syötä dokumentteja uudelleen:
   ```bash
   python scripts/ingest_documents.py data/documents/ --clear --recursive
   ```

#### "LLM-palvelu ei vastaa"

1. Tarkista Ollama-palvelun tila:
   ```bash
   docker logs llmfixu-ollama
   ```

2. Varmista että malli on ladattu:
   ```bash
   docker exec llmfixu-ollama ollama list
   ```

3. Lataa malli tarvittaessa:
   ```bash
   docker exec llmfixu-ollama ollama pull llama2
   ```

#### "Vektorietietokanta ei toimi"

1. Tarkista ChromaDB:n tila:
   ```bash
   docker logs llmfixu-chromadb
   ```

2. Käynnistä uudelleen:
   ```bash
   docker restart llmfixu-chromadb
   ```

### Suorituskyvyn optimointi

#### Mallien valinta

```bash
# Nopea mutta vähemmän tarkka
docker exec llmfixu-ollama ollama pull tinyllama

# Tasapainoinen
docker exec llmfixu-ollama ollama pull llama2

# Tarkka mutta hidas
docker exec llmfixu-ollama ollama pull llama2:13b
```

#### Chunk-asetusten säätö

Suuremmat dokumentit → Suurempi chunk-koko:
```bash
python scripts/ingest_documents.py /polku/ --chunk-size 2000 --chunk-overlap 400
```

Tarkempi haku → Pienempi chunk-koko:
```bash
python scripts/ingest_documents.py /polku/ --chunk-size 500 --chunk-overlap 100
```

## Integraatiot

### Python API

```python
from src.llmfixu.api.query_engine import QueryEngine

# Luo kysely-engine
engine = QueryEngine()

# Tee kysely
result = engine.query("Mitä dokumenteissa sanotaan?")
print(result['answer'])
```

### n8n Automaatio

1. Avaa n8n: http://localhost:5678
2. Kirjaudu: admin/changeme
3. Luo uusi workflow
4. Käytä HTTP Request -nodea kutsumaan Python-skriptejä

### REST API (kehitystyön alla)

Tulevassa versiossa:
```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Mitä dokumenteissa sanotaan?"}'
```

## Parhaita käytäntöjä

### Dokumenttien organisointi

1. **Lajittele aiheittain**:
   ```
   data/documents/
   ├── sopimukset/
   ├── raportit/
   ├── kasikirjat/
   └── arkisto/
   ```

2. **Käytä selkeitä tiedostonimiä**:
   - ✅ `audit_raportti_2024_Q1.pdf`
   - ❌ `raportti.pdf`

3. **Säännölliset päivitykset**:
   ```bash
   # Viikoittain
   python scripts/ingest_documents.py data/documents/uudet/ --recursive
   ```

### Kyselyiden muotoilu

1. **Ole spesifinen**:
   - ✅ "Mitä turvallisuusvaatimuksia järjestelmällä on?"
   - ❌ "Kerro turvallisuudesta"

2. **Käytä asiasanoja**:
   - ✅ "GDPR compliance vaatimukset"
   - ❌ "Tietosuoja-asiat"

3. **Pyydä lähteitä**:
   - ✅ "Listaa lähteet väitteelle"
   - ✅ Käytä `--verbose` -flagia

### Ylläpito

1. **Säännöllinen diagnostiikka**:
   ```bash
   # Päivittäin
   python scripts/diagnose_system.py >> logs/daily_health.log
   ```

2. **Varmuuskopiot**:
   ```bash
   # Viikottain
   docker run --rm -v llmfixu_chromadb_data:/data -v $(pwd):/backup ubuntu tar czf /backup/chromadb_$(date +%Y%m%d).tar.gz /data
   ```

3. **Lokien seuranta**:
   ```bash
   tail -f logs/llmfixu.log
   ```

## Edistyneet ominaisuudet

### Batch-prosessointi

```python
from src.llmfixu.api.query_engine import QueryEngine

engine = QueryEngine()
questions = [
    "Mitä riskejä on tunnistettu?",
    "Ketkä ovat vastuussa turvallisuudesta?",
    "Milloin seuraava auditointi tehdään?"
]

results = engine.batch_query(questions)
for q, r in zip(questions, results):
    print(f"Q: {q}")
    print(f"A: {r['answer']}\n")
```

### Mukautetut mallit

```bash
# Lataa erikoismalli
docker exec llmfixu-ollama ollama pull codellama

# Käytä kyselyssä
python scripts/query_system.py "Analysoi koodin laatua" --model codellama
```

Seuraavaksi: [API-dokumentaatio](api_dokumentaatio.md)
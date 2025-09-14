# LLMFixU Vianmääritysopas

## Yleisiä ongelmia ja ratkaisuja

### Docker-ongelmat

#### "Port already in use" -virhe

**Ongelma**: Docker-portti on jo käytössä
```
Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use
```

**Ratkaisu**:
```bash
# Tarkista käytössä olevat portit
sudo netstat -tulpn | grep -E ':(3000|8000|5678|11434)'

# Pysäytä ristiriitaiset palvelut
sudo kill -9 <PID>

# Tai muuta portteja .env-tiedostossa
nano .env
```

#### "Docker daemon not running" -virhe

**Ratkaisu**:
```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS
open /Applications/Docker.app

# Windows (WSL2)
# Käynnistä Docker Desktop
```

#### Konttien käynnistysongelmat

```bash
# Tarkista konttien tila
docker-compose ps

# Katso lokeja
docker-compose logs <service_name>

# Käynnistä uudelleen
docker-compose restart <service_name>

# Pakota uudelleenrakennus
docker-compose up --build -d
```

### Ollama-ongelmat

#### "Ollama service not available"

**Tarkistukset**:
```bash
# Kontin tila
docker logs llmfixu-ollama

# Palvelun testi
curl http://localhost:11434/api/tags

# Käynnistä uudelleen
docker restart llmfixu-ollama
```

#### Mallit eivät lataudu

```bash
# Listaa malleja
docker exec llmfixu-ollama ollama list

# Lataa malli manuaalisesti
docker exec llmfixu-ollama ollama pull llama2

# Testaa mallia
docker exec llmfixu-ollama ollama run llama2 "Testi"
```

#### GPU ei toimi

```bash
# Tarkista NVIDIA-tuki
nvidia-smi

# Asenna nvidia-docker
sudo apt-get install nvidia-docker2
sudo systemctl restart docker

# Testaa GPU-tuki
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### ChromaDB-ongelmat

#### "Connection refused" -virhe

```bash
# Tarkista kontin tila
docker logs llmfixu-chromadb

# Testaa yhteyttä
curl http://localhost:8000/api/v1/heartbeat

# Tarkista data-hakemisto
ls -la data/chroma/
sudo chown -R $USER:$USER data/chroma/
```

#### Tietokanta korruptoitunut

```bash
# Varmuuskopioi data
cp -r data/chroma data/chroma_backup

# Pysäytä ChromaDB
docker stop llmfixu-chromadb

# Tyhjennä data
rm -rf data/chroma/*

# Käynnistä uudelleen
docker start llmfixu-chromadb

# Syötä dokumentit uudelleen
python scripts/ingest_documents.py data/documents/ --clear --recursive
```

### Python-ongelmat

#### Riippuvuuksien asennusongelmat

```bash
# Päivitä pip
pip install --upgrade pip

# Asenna wheel
pip install wheel

# Asenna riippuvuudet uudelleen
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Virtuaaliympäristö
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### ModuleNotFoundError

```bash
# Tarkista PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Tai käytä -m flagia
python -m src.llmfixu.api.query_engine
```

#### Encoding-ongelmat

```bash
# Aseta UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Python-encoding
export PYTHONIOENCODING=utf-8
```

### Suorituskykyongelmat

#### Hidas LLM-generointi

**Optimointi**:
```bash
# Käytä pienempää mallia
docker exec llmfixu-ollama ollama pull tinyllama

# Säädä lämpötilaa
python scripts/query_system.py "Kysymys" --model tinyllama

# GPU-tuki
# Muokkaa docker-compose.yml lisäämään GPU-tuki
```

#### Muistiongelmiat

```bash
# Tarkista muistin käyttö
docker stats

# Rajoita Docker-muistia
docker update --memory="4g" llmfixu-ollama

# Kasvata swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Hidas vektorihaku

```bash
# Optimoi chunk-koko
python scripts/ingest_documents.py data/ --chunk-size 500 --chunk-overlap 50

# Vähennä kontekstidokumentteja
python scripts/query_system.py "Kysymys" --context-docs 2

# Indeksoi uudelleen
python -c "
from src.llmfixu.processors.vector_manager import VectorManager
vm = VectorManager()
vm.clear_collection()
"
python scripts/ingest_documents.py data/documents/ --recursive
```

### Tiedostokäsittelyongelmat

#### "File too large" -virhe

```bash
# Suurenna tiedostokokorajaa
nano .env
# Muuta: MAX_FILE_SIZE_MB=100

# Tai pienennä tiedostoa
pdftk large.pdf cat 1-10 output small.pdf
```

#### "Unsupported file format"

```bash
# Tarkista tuetut formaatit
python -c "
from src.llmfixu.config.settings import config
print(config.SUPPORTED_FORMATS)
"

# Konvertoi tiedosto
pandoc document.rtf -o document.docx
```

#### PDF-tekstin erottaminen epäonnistuu

```bash
# Asenna OCR-tuki
sudo apt-get install tesseract-ocr poppler-utils

# Käytä OCR:ää
pdf2image document.pdf | tesseract - output
```

### Verkko-ongelmat

#### Timeout-virheet

```bash
# Kasvata timeout-aikoja
python scripts/query_system.py "Kysymys" --timeout 120

# Tarkista palveluiden tila
python scripts/diagnose_system.py
```

#### Palomuuriongelmat

```bash
# Avaa portit (Ubuntu/Debian)
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw allow 5678
sudo ufw allow 11434

# Tarkista iptables
sudo iptables -L -n
```

## Lokien analysointi

### Docker-lokien tarkistus

```bash
# Kaikki palvelut
docker-compose logs

# Tietty palvelu
docker-compose logs ollama
docker-compose logs chromadb

# Seuraa reaaliaikaisesti
docker-compose logs -f ollama

# Viimeisimmät rivit
docker-compose logs --tail 50 ollama
```

### Python-lokien tarkistus

```bash
# Päälokit
tail -f logs/llmfixu.log

# Virhelokit
grep "ERROR" logs/llmfixu.log

# Tietyn päivän lokit
grep "2024-01-15" logs/llmfixu.log
```

### Järjestelmälokien tarkistus

```bash
# Docker daemon
sudo journalctl -u docker.service

# Systemd-palvelut
sudo systemctl status docker

# Dmesg-viestit
dmesg | grep -i error
```

## Diagnostiikkatyökalut

### Automaattinen diagnostiikka

```bash
# Kattava terveyden tarkistus
python scripts/diagnose_system.py --verbose

# JSON-muotoinen raportti
python scripts/diagnose_system.py --json > health_report.json

# Jatkuva monitorointi
watch -n 30 'python scripts/diagnose_system.py'
```

### Manuaalinen testaus

```bash
# Testaa jokainen komponentti erikseen

# 1. ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# 2. Ollama
curl http://localhost:11434/api/tags

# 3. OpenWebUI
curl http://localhost:3000

# 4. n8n
curl http://localhost:5678

# 5. Python API
python -c "
from src.llmfixu.api.query_engine import QueryEngine
engine = QueryEngine()
print(engine.health_check())
"
```

### Suorituskykytestit

```bash
# Latenssi-testi
time python scripts/query_system.py "Testikysymys"

# Dokumenttien latausaika
time python scripts/ingest_documents.py test_document.pdf

# Muistin käyttö
python -c "
import psutil
print(f'Muisti: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"
```

## Varmuuskopiointi ja palautus

### Tietokannan varmuuskopiointi

```bash
# ChromaDB varmuuskopiointi
docker run --rm \
  -v llmfixu_chromadb_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/chromadb_$(date +%Y%m%d).tar.gz /data

# Konfiguraatioiden varmuuskopiointi
tar czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

### Palautus

```bash
# ChromaDB palautus
docker-compose down
docker volume rm llmfixu_chromadb_data

docker run --rm \
  -v llmfixu_chromadb_data:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/chromadb_20240115.tar.gz -C /

docker-compose up -d
```

## Yleiset vianmäärityskomennot

### Ympäristön nollaus

```bash
#!/bin/bash
# reset_environment.sh

echo "Nollataan LLMFixU-ympäristö..."

# Pysäytä kaikki
docker-compose down --volumes --rmi all

# Poista data
rm -rf data/chroma/* logs/*

# Luo uudelleen
mkdir -p data/chroma data/documents logs

# Käynnistä uudelleen
docker-compose up -d

# Odota
sleep 30

# Testaa
python scripts/diagnose_system.py

echo "Ympäristö nollattu!"
```

### Debug-tila

```bash
#!/bin/bash
# debug_mode.sh

export LOG_LEVEL=DEBUG
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

echo "Debug-tila käytössä"
python scripts/diagnose_system.py --verbose

# Käynnistä interaktiivinen Python
python3 -c "
import sys
sys.path.insert(0, 'src')
from llmfixu.api.query_engine import QueryEngine
engine = QueryEngine()
print('Debug-sessio käynnissä. Käytä: engine.query(\"kysymys\")')
import code
code.interact(local=locals())
"
```

## Tuen hakeminen

### Tietojen kerääminen

Ennen tuen hakemista, kerää seuraavat tiedot:

```bash
# Järjestelmätiedot
echo "=== JÄRJESTELMÄTIEDOT ===" > debug_info.txt
uname -a >> debug_info.txt
docker --version >> debug_info.txt
docker-compose --version >> debug_info.txt
python3 --version >> debug_info.txt

# Palveluiden tila
echo "=== PALVELUIDEN TILA ===" >> debug_info.txt
docker-compose ps >> debug_info.txt

# Diagnostiikka
echo "=== DIAGNOSTIIKKA ===" >> debug_info.txt
python scripts/diagnose_system.py --json >> debug_info.txt

# Lokit
echo "=== DOCKER-LOKIT ===" >> debug_info.txt
docker-compose logs --tail 100 >> debug_info.txt

# Konfiguraatio (poista salaiset tiedot!)
echo "=== KONFIGURAATIO ===" >> debug_info.txt
cat .env | sed 's/SECRET_KEY=.*/SECRET_KEY=***HIDDEN***/' >> debug_info.txt
```

### GitHub Issue

Luo issue osoitteessa: https://github.com/mxxx222/llmfixu/issues

Sisällytä:
- Selkeä kuvaus ongelmasta
- Reprodusointiohjeet
- Järjestelmätiedot (debug_info.txt)
- Virheilmoitukset
- Mitä olet jo kokeillut

## Yhteenveto

Yleisimmät ongelmat ja nopeat ratkaisut:

1. **Palvelut eivät käynnisty** → Tarkista Docker ja portit
2. **LLM ei vastaa** → Varmista että mallit on ladattu
3. **Ei dokumentteja** → Syötä dokumentit uudelleen
4. **Hidas suorituskyky** → Käytä pienempiä malleja
5. **Muistiongelmia** → Rajoita Docker-resursseja

**Aina ensin**: `python scripts/diagnose_system.py`
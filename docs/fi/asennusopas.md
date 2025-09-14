# LLMFixU Asennusopas

## Järjestelmävaatimukset

### Vähimmäisvaatimukset

- **Käyttöjärjestelmä**: Linux, macOS, tai Windows (WSL2 suositeltu)
- **RAM**: 8 GB (16 GB suositeltu)
- **Tallennustila**: 10 GB vapaata tilaa
- **Docker**: Docker Engine 20.10+ ja Docker Compose v2
- **Python**: 3.8 tai uudempi

### Suositellut vaatimukset

- **RAM**: 16 GB tai enemmän
- **CPU**: 4+ ydintä
- **Tallennustila**: 50 GB SSD
- **GPU**: NVIDIA GPU CUDA-tuella (valinnainen, nopeuttaa LLM-prosessointia)

## Vaiheittainen asennus

### Vaihe 1: Esivaatimukset

#### Docker-asennus

**Ubuntu/Debian:**
```bash
# Päivitä pakettiluettelo
sudo apt update

# Asenna Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Lisää käyttäjä docker-ryhmään
sudo usermod -aG docker $USER

# Käynnistä uusi shell-sessio
newgrp docker
```

**macOS:**
```bash
# Asenna Docker Desktop
brew install --cask docker
```

**Windows (WSL2):**
1. Asenna Docker Desktop for Windows
2. Varmista että WSL2-integraatio on käytössä

#### Python-asennus

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
brew install python3
```

### Vaihe 2: Projektin lataus

```bash
# Kloonaa repositorio
git clone https://github.com/mxxx222/llmfixu.git
cd llmfixu

# Luo Python virtuaaliympäristö
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# tai: venv\Scripts\activate  # Windows
```

### Vaihe 3: Konfigurointi

```bash
# Kopioi ympäristömääritykset
cp .env.example .env

# Muokkaa konfiguraatiota
nano .env  # tai käytä muuta editoria
```

#### Tärkeät konfiguraatioparametrit

```bash
# Turvallisuus - VAIHDA NÄMÄ TUOTANTOYMPÄRISTÖSSÄ!
WEBUI_SECRET_KEY=your-unique-secret-key-here
N8N_BASIC_AUTH_PASSWORD=your-secure-password

# Palvelut (jos haluat muuttaa portteja)
OLLAMA_URL=http://localhost:11434
OPENWEBUI_URL=http://localhost:3000
CHROMADB_URL=http://localhost:8000
N8N_URL=http://localhost:5678

# Dokumenttien käsittely
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# AI-asetukset
DEFAULT_MODEL=llama2
TEMPERATURE=0.7
```

### Vaihe 4: Python-riippuvuudet

```bash
# Asenna riippuvuudet
pip install -r requirements.txt
```

### Vaihe 5: Docker-palveluiden käynnistys

```bash
# Käynnistä kaikki palvelut
docker-compose up -d

# Tarkista palveluiden tila
docker-compose ps
```

Odotettu tuloste:
```
NAME                   COMMAND                  SERVICE             STATUS              PORTS
llmfixu-chromadb       "/docker_entrypoint.…"   chromadb            running             0.0.0.0:8000->8000/tcp
llmfixu-n8n            "tini -- /docker-ent…"   n8n                 running             0.0.0.0:5678->5678/tcp
llmfixu-ollama         "/bin/ollama serve"      ollama              running             0.0.0.0:11434->11434/tcp
llmfixu-openwebui      "bash start.sh"          openwebui           running             0.0.0.0:3000->8080/tcp
```

### Vaihe 6: LLM-mallien lataus

```bash
# Lataa suositeltu malli
docker exec llmfixu-ollama ollama pull llama2

# Vaihtoehtoisesti, lataa pienempi malli
docker exec llmfixu-ollama ollama pull tinyllama

# Tai isompi, tarkempi malli
docker exec llmfixu-ollama ollama pull llama2:13b
```

### Vaihe 7: Järjestelmän testaus

```bash
# Aja täydellinen diagnostiikka
python scripts/diagnose_system.py

# Jos kaikki on kunnossa, näet:
# ✅ Dependencies: OK
# ✅ Configuration: OK
# ✅ Services: OK
# ✅ Vector database: OK
# ✅ LLM service: OK
# ✅ Integration test: OK
```

## Yleiset ongelmat ja ratkaisut

### 1. Docker-palvelut eivät käynnisty

**Ongelma**: Portit jo käytössä
```bash
# Tarkista käytössä olevat portit
sudo netstat -tulpn | grep -E ':(3000|8000|5678|11434)'

# Pysäytä ristiriitaiset palvelut tai muuta portteja .env-tiedostossa
```

**Ongelma**: Riittämätön muisti
```bash
# Tarkista muistin käyttö
docker stats

# Pysäytä tarpeettomat kontit
docker container prune
```

### 2. Ollama-mallit eivät lataudu

```bash
# Tarkista Ollama-kontin tila
docker logs llmfixu-ollama

# Käynnistä kontti uudelleen
docker restart llmfixu-ollama

# Kokeile manuaalista latausta
docker exec -it llmfixu-ollama ollama pull llama2
```

### 3. ChromaDB-yhteysongelmat

```bash
# Tarkista tietokannan tila
docker logs llmfixu-chromadb

# Luo data-hakemisto manuaalisesti
mkdir -p data/chroma
chmod 755 data/chroma
```

### 4. Python-riippuvuusongelmat

```bash
# Päivitä pip
pip install --upgrade pip

# Asenna riippuvuudet uudelleen
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## GPU-tuki (valinnainen)

Jos haluat käyttää NVIDIA GPU:ta LLM-prosessointiin:

### 1. Asenna NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 2. Muokkaa docker-compose.yml

Lisää Ollama-palveluun:
```yaml
ollama:
  # ... muut asetukset
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### 3. Käynnistä palvelut uudelleen

```bash
docker-compose down
docker-compose up -d
```

## Tietoturvasuositukset

### Tuotantokäyttöön

1. **Vaihda oletussalasanat**:
   ```bash
   # Luo vahvat salasanat
   openssl rand -base64 32  # WEBUI_SECRET_KEY
   openssl rand -base64 16  # N8N_BASIC_AUTH_PASSWORD
   ```

2. **Käytä HTTPS:ää**:
   - Asenna käänteinen välityspalvelin (nginx/Apache)
   - Hanki SSL-sertifikaatti (Let's Encrypt)

3. **Rajoita verkkoliikenne**:
   ```bash
   # Muokkaa docker-compose.yml:
   # Poista portit, jotka eivät tarvitse ulkoista yhteyttä
   ```

4. **Säännölliset varmuuskopiot**:
   ```bash
   # Tietokannan varmuuskopio
   docker run --rm -v llmfixu_chromadb_data:/data -v $(pwd):/backup ubuntu tar czf /backup/chromadb_backup.tar.gz /data
   ```

## Päivitys

```bash
# Lataa uusin versio
git pull origin main

# Päivitä riippuvuudet
pip install -r requirements.txt --upgrade

# Päivitä Docker-imaget
docker-compose pull
docker-compose up -d
```

## Asennus valmis!

Kun asennus on valmis, voit:

1. **Käyttää web-käyttöliittymää**: http://localhost:3000
2. **Syöttää dokumentteja**: `python scripts/ingest_documents.py data/documents/`
3. **Tehdä kyselyitä**: `python scripts/query_system.py -i`
4. **Seurata diagnostiikkaa**: `python scripts/diagnose_system.py`

Seuraavaksi: [Käyttöohje](kayttoohje.md)
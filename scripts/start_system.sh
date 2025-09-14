#!/bin/bash
"""
LLMFixU käynnistysskripti - Käynnistää koko järjestelmän.
"""

set -e

# Värit tulostukseen
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                         LLMFixU                              ║"
echo "║                   AI Audit System                           ║"
echo "║                                                              ║"
echo "║               Käynnistysskripti                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Tarkista Docker
echo -e "${YELLOW}Tarkistetaan Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Virhe: Docker ei ole asennettu${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Virhe: Docker Compose ei ole asennettu${NC}"
    exit 1
fi

# Tarkista Python
echo -e "${YELLOW}Tarkistetaan Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Virhe: Python 3 ei ole asennettu${NC}"
    exit 1
fi

# Luo ympäristömääritykset jos ei ole olemassa
if [ ! -f .env ]; then
    echo -e "${YELLOW}Luodaan .env-tiedosto...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env-tiedosto luotu. Muokkaa sitä tarpeen mukaan.${NC}"
fi

# Luo hakemistot
echo -e "${YELLOW}Luodaan hakemistot...${NC}"
mkdir -p data/documents data/chroma logs

# Käynnistä Docker-palvelut
echo -e "${YELLOW}Käynnistetään Docker-palvelut...${NC}"
docker-compose down 2>/dev/null || true
docker-compose pull
docker-compose up -d

# Odota että palvelut käynnistyvät
echo -e "${YELLOW}Odotetaan palveluiden käynnistymistä...${NC}"
sleep 10

# Tarkista palvelut
echo -e "${YELLOW}Tarkistetaan palvelut...${NC}"

services=("ollama:11434" "chromadb:8000" "openwebui:3000" "n8n:5678")
all_ok=true

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    
    if curl -s -f http://localhost:$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name (port $port): OK${NC}"
    else
        echo -e "${RED}❌ $name (port $port): FAILED${NC}"
        all_ok=false
    fi
done

if [ "$all_ok" = false ]; then
    echo -e "${RED}Jotkut palvelut eivät käynnistyneet. Tarkista docker-compose logs.${NC}"
    exit 1
fi

# Asenna Python-riippuvuudet
echo -e "${YELLOW}Asennetaan Python-riippuvuudet...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
fi

pip install -r requirements.txt

# Lataa oletusmallit
echo -e "${YELLOW}Ladataan LLM-malleja...${NC}"
echo "Tämä voi kestää useita minuutteja..."

# Tarkista onko malleja jo ladattu
if docker exec llmfixu-ollama ollama list | grep -q "llama2"; then
    echo -e "${GREEN}✅ llama2 on jo ladattu${NC}"
else
    echo -e "${YELLOW}Ladataan llama2...${NC}"
    docker exec llmfixu-ollama ollama pull llama2
    echo -e "${GREEN}✅ llama2 ladattu${NC}"
fi

# Käynnistä diagnostiikka
echo -e "${YELLOW}Ajetaan järjestelmädiagnostiikka...${NC}"
python scripts/diagnose_system.py

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    KÄYNNISTYS VALMIS!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}Palveluiden osoitteet:${NC}"
echo "• OpenWebUI (LLM-käyttöliittymä): http://localhost:3000"
echo "• ChromaDB (vektorietietokanta): http://localhost:8000"
echo "• n8n (automaatio): http://localhost:5678 (admin/changeme)"
echo "• Ollama API: http://localhost:11434"

echo -e "${BLUE}Seuraavat vaiheet:${NC}"
echo "1. Syötä dokumentteja:"
echo "   python scripts/ingest_documents.py data/documents/ --recursive"
echo ""
echo "2. Tee kyselyitä:"
echo "   python scripts/query_system.py -i"
echo ""
echo "3. Käytä web-käyttöliittymää:"
echo "   Avaa http://localhost:3000 selaimessa"

echo -e "${GREEN}Järjestelmä on käytettävissä!${NC}"
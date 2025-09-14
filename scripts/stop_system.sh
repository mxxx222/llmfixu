#!/bin/bash
"""
LLMFixU pysäytysskripti - Pysäyttää koko järjestelmän.
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
echo "║               Pysäytysskripti                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Pysäytä Docker-palvelut
echo -e "${YELLOW}Pysäytetään Docker-palvelut...${NC}"
docker-compose down

echo -e "${GREEN}✅ Kaikki palvelut pysäytetty${NC}"

# Valinnaiset toiminnot
read -p "Haluatko poistaa Docker-imaget? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Poistetaan Docker-imaget...${NC}"
    docker-compose down --rmi all
    echo -e "${GREEN}✅ Imaget poistettu${NC}"
fi

read -p "Haluatko poistaa tietokannat? VAROITUS: Kaikki dokumentit poistetaan! (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Poistetaan tietokannat...${NC}"
    docker-compose down --volumes
    sudo rm -rf data/chroma/*
    echo -e "${GREEN}✅ Tietokannat poistettu${NC}"
fi

echo -e "${GREEN}LLMFixU pysäytetty.${NC}"
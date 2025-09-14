#!/bin/bash
# Automatinen asennusskripti LLMFixU-järjestelmälle

set -e

echo "🚀 LLMFixU Auditointi-AI järjestelmän asennus"
echo "============================================="

# Tarkista Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker ei ole asennettu. Asenna Docker ensin."
    exit 1
fi

echo "✅ Docker löydetty"

# Tarkista Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python ei ole asennettu. Asenna Python 3.8+ ensin."
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✅ Python löydetty"

# Asenna Python-riippuvuudet
echo "📦 Asennetaan Python-riippuvuudet..."
$PYTHON_CMD -m pip install -r requirements.txt

# Käynnistä palvelut
echo "🐳 Käynnistetään Docker-palvelut..."
docker compose up -d

echo "⏳ Odotetaan palveluiden käynnistymistä (30 sekuntia)..."
sleep 30

# Lataa perusmalli
echo "🤖 Ladataan perusmalli Ollamaan..."
docker exec ollama ollama pull llama2:7b || echo "⚠️ Mallin lataus epäonnistui, voit kokeilla myöhemmin komennolla 'make pull-models'"

# Suorita diagnostiikka
echo "🔍 Suoritetaan diagnostiikka..."
$PYTHON_CMD scripts/diagnostic.py

echo ""
echo "🎉 Asennus valmis!"
echo ""
echo "Käyttöliittymät:"
echo "- OpenWebUI: http://localhost:3000"
echo "- n8n: http://localhost:5678"
echo "- ChromaDB API: http://localhost:8000"
echo "- Ollama API: http://localhost:11434"
echo ""
echo "Hyödyllisiä komentoja:"
echo "- make help          # Näytä kaikki komennot"
echo "- make diag          # Tarkista järjestelmän tila"
echo "- make embed         # Tallenna dokumentteja"
echo "- make query         # Hae dokumentteja"
echo "- make logs          # Näytä palveluiden lokit"
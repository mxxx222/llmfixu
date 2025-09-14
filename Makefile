.PHONY: help start stop diag clean

help: ## Näytä tämä ohje
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

start: ## Käynnistä kaikki palvelut
	docker compose up -d
	@echo "Palvelut käynnistetty. Odota hetki ja aja 'make diag' tarkistaaksesi tilan."

stop: ## Pysäytä kaikki palvelut
	docker compose down

restart: ## Käynnistä palvelut uudelleen
	docker compose down
	docker compose up -d

diag: ## Tarkista palveluiden tila ja yhteydet
	@echo "=== Docker-kontit ==="
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(ollama|chroma|openwebui|n8n)" || echo "Ei löytynyt palveluita"
	@echo "\n=== Yksityiskohtainen diagnostiikka ==="
	@python scripts/diagnostic.py

install-deps: ## Asenna Python-riippuvuudet
	pip install -r requirements.txt

logs: ## Näytä palveluiden lokit
	docker compose logs -f

embed: ## Käynnistä embedding-skripti
	python scripts/embed.py

query: ## Käynnistä query-skripti
	python scripts/query.py

pdf: ## Käynnistä PDF-käsittelyskripti
	python scripts/pdf.py

pull-models: ## Lataa suositut mallit Ollamaan
	docker exec ollama ollama pull llama2:7b
	docker exec ollama ollama pull orca-mini:3b
	docker exec ollama ollama pull codellama:7b

clean: ## Poista kaikki Docker-tiedot (VAROITUS: poistaa kaikki tiedot!)
	docker compose down -v
	docker system prune -f
.PHONY: up diag embed

up:
	docker compose down
	docker compose up -d

diag:
	curl $$CHROMA_HOST/api/v1/heartbeat
	curl $$OLLAMA_HOST/api/tags

embed:
	ollama pull $$EMBED_MODEL
	python embed_to_chroma.py docs/example.pdf

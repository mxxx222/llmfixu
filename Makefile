diag:
	@docker compose ps
	@echo "---- PORTS ----"
	@docker ps --format "table {{.Names}}	{{.Ports}}	{{.Status}}"
	@echo "---- CURL ----"
	-@curl -sS http://127.0.0.1:11434/api/tags || true
	-@curl -sS http://127.0.0.1:8000/api/v1/heartbeat || true
	-@curl -sSI http://127.0.0.1:8080 || true
	-@curl -sSI http://127.0.0.1:5678 || true

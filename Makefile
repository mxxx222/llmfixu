diag:
	@docker ps --format "table {{.Names}}	{{.Ports}}	{{.Status}}"
	@curl -s http://127.0.0.1:11434/api/tags || true
	@curl -s http://127.0.0.1:8000/api/v1/heartbeat || true
	@curl -I http://127.0.0.1:8080 || true
	@curl -I http://127.0.0.1:5678 || true

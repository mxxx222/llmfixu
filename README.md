# llmfixu

## macOS Docker CLI path fix

Docker Desktop may install the Docker CLI outside of your shell's `PATH`.
If `docker` or `docker compose` commands are not found, run these steps:

1. Ensure Docker Desktop is running.
2. Create symlinks to the Docker binaries and reload your shell:

   ```sh
   which docker; docker --version || true

   sudo mkdir -p /usr/local/bin ~/.docker/cli-plugins

   sudo ln -sf "/Applications/Docker.app/Contents/Resources/bin/docker" \
     /usr/local/bin/docker

   sudo ln -sf "/Applications/Docker.app/Contents/Resources/cli-plugins/docker-compose" \
     ~/.docker/cli-plugins/docker-compose

   exec zsh -l

   docker --version
   docker compose version
   ```
3. Start services and run diagnostics:

   ```sh
   docker compose up -d
   docker ps
   make diag
   ```

   Ports 11434, 8000, 8080, and 5678 should be listening and curl tests should
   succeed.

4. Open in a browser:
   - OpenWebUI: <http://127.0.0.1:8080>
   - n8n: <http://127.0.0.1:5678>

If `docker compose up -d` still fails, provide diagnostic output:

```sh
docker context ls
docker info
docker compose logs --no-log-prefix ollama
```


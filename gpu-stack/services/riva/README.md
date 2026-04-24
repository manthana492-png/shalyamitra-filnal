# NVIDIA Riva in this stack

## Why the container looped with exit code 0

The **`nvcr.io/nvidia/riva/riva-speech`** image is **not** meant to be started as a bare `docker run`/`compose` service without the **Riva Quick Start** flow. NVIDIA’s flow is:

1. **`bash riva_init.sh`** — downloads models from NGC (needs **`NGC_API_KEY`**), prepares Triton model repo.
2. **`bash riva_start.sh`** — starts the Riva / Triton stack (often orchestrates containers + mounts).

If Compose starts only the image with no initialized model directory and no start script, the default process can **print the banner and exit immediately** → Docker shows **`Restarting (0)`** and logs repeat the header.

**Docs:** [Local (Docker) — Riva](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/installation/deploy-local.html)

## How we run it in this repo

- **`riva`** is behind Compose **profile `nvidia`**. Default:

  ```bash
  docker compose -f docker-compose.gpu.yml up -d
  ```

  does **not** start Riva (avoids a crash loop when models aren’t ready).

- To **try** Riva + Holoscan on GPU:

  ```bash
  export NGC_API_KEY="your-ngc-key"
  COMPOSE_PROFILES=nvidia docker compose -f docker-compose.gpu.yml up -d
  ```

  You still need a **valid Riva deployment** (Quick Start on the host, or follow NVIDIA’s compose for your version). After **`riva_init`**, adjust **`command`/`volumes`** in `docker-compose.gpu.yml` to match what `riva_start.sh` uses for your release.

- The **agent** does **not** hard-depend on Riva: ASR falls back to cloud tiers if Riva is down.

## Config mount

`./services/riva` is mounted to `/config` on the Riva container for custom config when your deployment supports it.

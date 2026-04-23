# Riva local config (optional)

Mount this directory for custom Riva configuration files when not using the default
container entrypoint. The compose file bind-mounts `./services/riva` to `/config` on the
Riva container. Leave empty to use the image defaults.

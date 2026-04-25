# Thin root entrypoint for repository tasks.
# Keep this file at the repo root so plain `make <target>` works.

include make/docker.mk
include make/node.mk

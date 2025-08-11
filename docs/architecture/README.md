This folder contains architecture diagrams.

Files:
- `system-context.puml`
- `components.puml`

Render:
- Docker: `docker run --rm -v $(pwd):/data think/plantuml -tsvg /data/system-context.puml`
- Docker: `docker run --rm -v $(pwd):/data think/plantuml -tsvg /data/components.puml`
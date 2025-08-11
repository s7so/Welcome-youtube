This folder contains flowcharts for key user stories/processes.

- Source (PlantUML): `us-03-sync-attendance.puml`
- Output (to be generated): `us-03-sync-attendance.svg`

How to render locally:
- Using Docker: `docker run --rm -v $(pwd):/data think/plantuml -tsvg /data/us-03-sync-attendance.puml`
- Or with Java + PlantUML CLI: `plantuml -tsvg us-03-sync-attendance.puml`
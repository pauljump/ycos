# ycos project contract

`ycos` is a portable, offline snapshot of 6,120 YC company records collected on
September 21–22, 2026. Its canonical source root is `/Users/mini-home/projects/ycos`.
It is an independent data repository requested by Paul, with no running service,
shared package dependency, deployment, billing, or runtime credentials.

Portfolio policy lives at `../_factory/control-plane/AGENT-CORE.md` in Paul's workspace.
Dataset contents, provenance, and the read interface are documented in `README.md`
and `SCHEMA.md`. `data/companies.json` is the stable consumer entry point.

The source archive remains separately preserved. Exporting is offline; do not
silently replace the snapshot with a live scrape. Preserve provenance, coverage
limits, and the distinctions between directory and YC source fields.

Verify data changes with `python3 scripts/validate.py`. Regeneration uses
`python3 scripts/export.py /path/to/original/companies.jsonl`.

# AGENTS.md — DOX Framework

## Purpose

Curated collection of 1,371+ research papers on Autism Spectrum Disorder (ASD), Tourette Syndrome, ADHD, and related neurodevelopmental conditions. Includes acquisition scripts, metadata, patient-friendly summaries, and category organization.

## Ownership

Research corpus + Python tooling for acquisition and cleanup. Not a service.

## Local Contracts

- Papers live under `acquired_papers/` organized by category
- Acquisition scripts in root (`extract_papers.py`) and `scripts/`
- Config in `config/`
- Python deps: `requests`, `beautifulsoup4`, `lxml`, `PyYAML`
- GitHub remote: `AtticusG3/ASD-Research-Papers`
- Large repo with backup dirs — do not `git add -A` without scoping

## Work Guidance

- Adding new papers: extend `extract_papers.py` scripts, not manual placement
- Category structure defined in config — match existing taxonomy
- Backup dirs (`backup_originals/`, `final_cleanup_backup/`, `duplicate_cleanup_backup/`) are historical artifacts — do not commit new content there

## Verification

No automated verification framework. Manual: check Python scripts parse cleanly, no broken symlinks in paper dirs.

## Child DOX Index

None yet

---
*DOX framework: re-read this file before editing any path in this subtree. Closer docs override parents but never weaken DOX.*

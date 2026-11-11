# Changelog

All notable changes to XMind MD are documented in this file.

This project is pre-1.0. Releases may change the Markdown subset, the IR contract, or the XMind export profile. See the release notes and capability documentation before using it in production.

## [0.1.0] - 2026-11-11 — Alpha

First public pre-1.0 release candidate of the Markdown-to-XMind pipeline.

### Added
- Enriched Markdown parser with YAML front matter and XMind directives.
- Neutral IR 1.0.0 model, JSON Schema, serialization and semantic validation.
- IR style resolver with embedded and external YAML style catalogs.
- JSON and modern XMind workbook exporters.
- `xmind-md` command-line interface, including format selection and version reporting.
- Examples, style configuration, technical specifications and development documentation.
- MIT license and third-party provenance notices.
- GitHub Actions quality, compatibility, packaging and installed-distribution smoke tests.

### Improved
- Validation and preservation of IR metadata and extensions.
- JSON-compatible YAML normalization and stricter invalid-value handling.
- Relationship line styling and XMind capability validation.
- Wheel and source distribution verification, clean installation and CLI conversion tests.

### Known limitations
- The Markdown parser implements a documented subset; it is not a complete CommonMark/GFM implementation.
- The XMind exporter is partial. It does not export resources/images, tasks, boundaries, summaries, extensions, or `Topic.kind=summary`.
- Content blocks are flattened into XMind notes, so block structure and some inline formatting are lost.
- The latest style-enhanced smoke has passed automated structural checks; manual inspection in XMind Desktop is still required for this release candidate.
- CI runs on Ubuntu. Python 3.10 remains in the compatibility matrix although upstream support ended on 2026-10-01; distribution installation is tested on Python 3.12.
- The third-party inventory documents direct dependencies and identified fixtures, but is not a complete transitive SBOM.

### Validation
- 161 tests pass on each of Python 3.10, 3.11 and 3.12.
- Ruff lint and format checks pass on all three matrix versions.
- Wheel and sdist build, verify, install in clean Python 3.12 environments, and generate JSON/XMind through the installed CLI.
- XMind output passes ZIP, MIME and JSON structural checks.

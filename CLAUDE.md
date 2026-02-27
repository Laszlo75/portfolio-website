# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands

```bash
quarto render          # Render the full website to _site/
quarto preview         # Live preview with hot reload
quarto render cv.qmd   # Render PDF CV separately (excluded from site build)
```

The site build excludes `cv.qmd` (Typst PDF output) — it must be rendered independently.

## Architecture

This is a Quarto website (`project: type: website`) for an academic portfolio. Theme: Bootstrap `flatly` with extensive custom overrides in `styles.css`.

### Data-Driven CV (Single Source of Truth)

Six CSV files in `data/` drive three different CV outputs:

```
data/*.csv
  ├→ resume.qmd      — HTML CV (simple markdown via cv_entry())
  ├→ resume-v2.qmd   — HTML CV (timeline visual via cv_entry_html())
  └→ cv.qmd          — PDF CV (Typst via typstcv::resume_entry())
```

Update CSV data once → all three regenerate. CSV schemas:
- `education.csv`, `work.csv`: title, description, location, start, end
- `qualifications.csv`: title, description, location, date, detail
- `roles.csv`: title, organisation, date
- `research.csv`: acronym, title
- `skills.csv`: category, description

### Key Files

- `_quarto.yml` — Site config: navbar, footer, theme, analytics
- `_variables.yml` — Shared variables (orcid, email), used via `{{< var name >}}`
- `styles.css` — Full design system with CSS variables, fonts, animations
- `assets/my-publication-list.bib` — Bibliography parsed by R `bibtex` package
- `publications.qmd` — R-rendered publication cards with year grouping, action buttons, expandable abstracts

### Extensions

- **fontawesome** (`quarto-ext/fontawesome` v1.3.0) — `{{< fa icon >}}` shortcodes
- **awesomecv-typst** (`kazuyanagimoto/awesomecv` v0.1.0) — Typst CV template for `cv.qmd`

### R Dependencies

- `glue` — used in resume.qmd and resume-v2.qmd for string interpolation
- `bibtex` — used in publications.qmd to parse .bib file
- `typstcv` — used in cv.qmd for Typst CV formatting (`format_date()`, `resume_entry()`)

### Updating Publications

1. Update your Zotero library (add DOI, PMID, abstract for each entry)
2. Export from Zotero using **Better BibTeX** format (not BibTeX, not BibLaTeX)
   - Better BibTeX uses `year` and `journal` fields that `read.bib()` expects
   - Standard BibTeX wraps every title word in `{braces}`, Better BibTeX only wraps acronyms in `{{double braces}}`
3. Save as `assets/my-publication-list.bib`
4. Run `quarto render publications.qmd` to rebuild

## Conventions

- R code chunks in .qmd files use `output: asis` to emit raw markdown/HTML
- Don't use `cat()` to write to console — use it only with `output: asis` chunks to write directly into the document
- Blog posts live in `posts/` with `freeze: true` (cached execution)
- CSS uses custom properties: `--accent` (#1a7a8a teal), `--heading-color`, etc.
- Fonts: Source Serif 4 (headings), Source Sans 3 (body) via Google Fonts
- Never modify `_site/` directly — it's generated output

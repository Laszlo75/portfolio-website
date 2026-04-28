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

This is a Quarto website (`project: type: website`) for an academic portfolio at [lszabo.me](https://lszabo.me). Theme: Bootstrap `flatly` with extensive custom overrides in `styles.css`.

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

## Blog

### Content Strategy

Three interconnected pillars, publishing twice monthly:

1. **AI for Clinical Research** — Claude skills, literature search, protocol review, governance
2. **R & Data Science for NHS Clinicians** — survival analysis, data pipelines, transplant outcomes
3. **Academic Tools & Workflows** — Quarto, Obsidian, reproducible research

Target audience: clinician-coders, AI-curious researchers, academic portfolio builders.
Full strategy documented in Obsidian at `01 Projects/Blog/BLOG-STRATEGY.md`.

### Blog File Structure

```
posts/
├── ai-literature-search/index.qmd    # Using Claude for Medical Literature Search
├── literature-review-skill/index.qmd  # From Manual Search to Automated Evidence Pipeline
├── plans/index.qmd                    # Hello World
└── [new-post]/index.qmd              # Each post in its own directory
briefs/                                # /blog brief output stored here
assets/
└── schema-blogpost-*.html             # JSON-LD schema per post
```

### Published Posts

| Slug | Title | Published |
|------|-------|-----------|
| `plans` | Why a transplant surgeon built an academic site with Quarto | 8 Feb 2026 |
| `ai-literature-search` | Claude for medical literature search: Avoid hallucinations | 3 Mar 2026 |
| `literature-review-skill` | From manual search to automated evidence pipeline | 4 Apr 2026 |
| `search-result-to-structured-doc` | From search results to structured document | 28 Apr 2026 (draft) |

**Title style**: sentence case (capitalise first word, proper nouns, and the first word after a colon — everything else lowercase).

### Post Frontmatter Template

Every blog post must include:

```yaml
title: "Post Title"
subtitle: "Optional subtitle"
description: "Meta description — max 160 chars, for SEO and AI citation"
author: "Laszlo Szabo"
date: "YYYY-MM-DD"
date-modified: "YYYY-MM-DD"
categories: [AI, research methods, ...]
image: hero.jpg
fig-alt: "Descriptive alt text for hero image"
citation: true
draft: false
```

**Critical**: Always set `date` to an explicit date string. Never use `date: today` or `date: last-modified` — these cause the publication date to change on every render.

### Post Conventions

- Each post lives in `posts/[slug]/index.qmd`
- Hero image: `posts/[slug]/hero.jpg` (compressed <200KB, 1200×675)
- Figures: use Quarto syntax `![Caption](image.png){fig-alt="..." width="80%"}`
- `citation: true` in YAML auto-generates a citation block at post footer
- Schema: place JSON-LD in `assets/schema-blogpost-[slug].html`, include via `include-in-header`
- Internal links: always cross-link to related posts, `/publications.qmd`, `/resume.qmd`

### Writing Style

- Tone: peer-level clinical writing, authoritative not patronising, first-person where experience is relevant
- Answer-first formatting: every H2 opens with a 40-60 word stat-rich paragraph
- Citation capsules: 5 self-contained passages per post, optimised for AI extraction
- All statistics must have inline source attribution with tier 1-2 citations
- No AI-detectable phrasing — write like a surgeon, not like an LLM

### Blog Pipeline Commands (claude-blog toolkit)

These `/blog` slash commands are available via the AgriciDaniel/claude-blog plugin:

| Stage | Command | Output |
|-------|---------|--------|
| Plan | `/blog brief "topic"` | Markdown brief → save to `briefs/` |
| Plan | `/blog outline "topic"` | SERP-informed H2/H3 outline |
| Plan | `/blog calendar` | Monthly content calendar |
| Write | `/blog write "topic"` | Full `.qmd` draft in `posts/[slug]/` |
| Review | `/blog analyze post.qmd` | 100-point quality score (target: 80+) |
| Review | `/blog seo-check post.qmd` | SEO checklist: title, meta, headings, links |
| Review | `/blog factcheck post.qmd` | Verify statistics against cited sources |
| Review | `/blog geo post.qmd` | AI citation optimisation audit |
| Distribute | `/blog repurpose post.qmd` | LinkedIn article + X thread |
| Metadata | `/blog schema post.qmd` | JSON-LD for BlogPosting + FAQ |

**Quarto adaptations**: The claude-blog toolkit targets WordPress/Ghost/Shopify. For this site:
- Ignore `/blog taxonomy` — not applicable
- Schema output goes to `assets/`, not inline
- Image syntax must use Quarto figure format, not HTML `<img>`
- `citation: true` handles citing; don't duplicate with schema

### Evidence Research for Clinical Posts

For posts requiring clinical evidence (PubMed, guidelines), the `literature-search` skill runs in **Claude.ai** (not Claude Code) because it needs PubMed and Scholar Gateway MCPs. Workflow:

1. Run `/blog brief` here in Claude Code → get outline and keywords
2. Switch to Claude.ai → run literature search with the clinical question
3. Save evidence summary + BibTeX to the post directory
4. Return here → run `/blog write` with brief + evidence as context

### Obsidian Vault Integration

The editorial planning lives in a separate Obsidian vault. When writing or planning blog posts, consult these notes via the Obsidian MCP:

| Obsidian note | Purpose |
|---------------|---------|
| `01 Projects/Blog/Content Pipeline.md` | Per-post status tracker — update after each workflow step |
| `01 Projects/Blog/BLOG-CALENDAR.md` | Editorial calendar with dates and distribution schedule |
| `01 Projects/Blog/BLOG-STRATEGY.md` | Three-pillar strategy, audience segments, competitive landscape |
| `01 Projects/Blog/Blog Series Index.md` | Protocol Reviewer series tracking |
| `01 Projects/Blog/briefs/` | Stored briefs from `/blog brief` runs |
| `01 Projects/Blog/Post N - *.md` | Draft outlines and planning notes per post |

**After every blog workflow step**, update the Obsidian vault:
1. Update **Content Pipeline** — change post status, add `/blog analyze` score, fill in live URL
2. If publishing, add to the **Published posts** table with freshness due date (30 days)
3. Log the action in today's **daily note** with `#blog` tag

### Quality Gates (Pre-Publish Checklist)

Before `quarto render` and `git push`:
- [ ] `/blog analyze` score ≥ 80
- [ ] `/blog factcheck` — all claims verified
- [ ] `/blog seo-check` — no critical issues
- [ ] `/blog geo` — AI citation capsules present
- [ ] `date` field is explicit (not `today`)
- [ ] `draft: false` is set
- [ ] `citation: true` in YAML
- [ ] Hero image <200KB, has `fig-alt`
- [ ] All internal links resolve
- [ ] Quarto renders without warnings
- [ ] Content Pipeline note updated in Obsidian
- [ ] Daily note logged in Obsidian with `#blog`

## Conventions

- R code chunks in .qmd files use `output: asis` to emit raw markdown/HTML
- Don't use `cat()` to write to console — use it only with `output: asis` chunks to write directly into the document
- Blog posts live in `posts/` with `freeze: true` (cached execution)
- CSS uses custom properties: `--accent` (#1a7a8a teal), `--heading-color`, etc.
- Fonts: Source Serif 4 (headings), Source Sans 3 (body) via Google Fonts
- Never modify `_site/` directly — it's generated output

## Deployment

```bash
quarto render
git add -A && git commit -m "Post: [title]"
git push               # Vercel auto-deploys from main
```

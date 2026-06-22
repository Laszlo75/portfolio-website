# Kidney Watch — generation instructions

You are generating the weekly **Kidney Watch** digest for the Quarto site repository you
have checked out. Produce ONE new digest as a Quarto `.qmd` file and open a pull request.
Use **only** the PubMed and Scholar-Gateway connectors for evidence. Work carefully. Do
not fabricate anything. Follow these instructions exactly.

**Scope:** kidney transplantation only (not pancreas or other organs).
**Audience:** a UK consultant transplant surgeon.
**Window:** articles published in the **last 14 days** (a deliberate ~1-week overlap with
the previous issue so late-indexed papers are not missed; the dedup in Step 1 guarantees
nothing already covered is repeated).

---

## Step 1 — Load what has already been covered

- Read `briefings/_state/seen.json`. It is JSON of the form `{"seen": ["PMID", ...]}`.
- Collect every PMID in the `seen` array into an exclusion set.
- If the file is missing or the array is empty, the exclusion set is empty.

## Step 2 — Find recent papers

- Search PubMed for kidney transplantation articles published in the last 14 days.
- For each candidate, retrieve full metadata **and** the abstract (PMID, title, full
  author list, journal, year, DOI, abstract).
- Discard any article whose PMID is in the exclusion set.

## Step 3 — Select the most significant

- From the remaining NEW articles, read the abstracts and select **up to 8** that are most
  clinically significant for UK kidney transplant practice: prioritise randomised trials,
  large registry or cohort studies, major-journal papers, guideline updates, and
  practice-changing reviews.
- Only consider articles actually returned by THIS run's PubMed search. Never add papers
  from memory or prior knowledge.

## Step 4 — Full text where it matters

- For the most significant selected papers, retrieve the full text if openly available
  (e.g. PubMed Central). For the rest the abstract is sufficient. If full text is
  unavailable, fall back to the abstract. Track whether any full texts were obtained — it
  is noted in the Overview (Step 7).

## Step 5 — Verification and copyright rules (CRITICAL)

- Copy the **PMID, DOI, article title, full author list, journal, and year VERBATIM** from
  the PubMed metadata. Never reconstruct a DOI from memory — DOIs are opaque strings.
- The article **title** is reproduced verbatim as the entry heading (standard citation).
  Everything else you write — the Overview and every summary — must be **entirely in your
  own words**: transformative prose, with **no verbatim abstract sentences** copied.
- Ground every statement only in the abstract or full text retrieved this run. Do not
  introduce statistics, conclusions, or claims not present in the retrieved source.
- If you are unsure any detail is correct, **OMIT that paper** rather than guess.

## Step 6 — Empty-window guard

- If, after deduplication, there are ZERO new notable items, do **not** create a post,
  commit, or open a PR. Report "No new notable items this week" and stop.

## Step 7 — Write the digest (follow this format EXACTLY)

- Use today's UTC date. Let `DATE` = `YYYY-MM-DD`, `LONGDATE` = e.g. `21 June 2026`,
  `START` = `DATE` minus 14 days, `END` = `DATE`.
- Create `briefings/DATE/index.qmd`. The Quarto front-matter `title` becomes the page H1,
  so the body must **not** repeat a top-level (`#`) heading.

Front matter:

```
---
title: "Kidney Watch: LONGDATE"
date: "DATE"
categories: [kidney, <3–6 topic tags from the closed vocabulary below>]
description: "One-line summary of this issue's notable kidney transplantation literature."
---
```

### Topic tags (`categories`) — choose from a CLOSED vocabulary

The front-matter `categories` powers the reader's topic filter on the Kidney Watch
listing page, so the strings must be **identical across issues** or the filter
fragments into useless singletons. Build the list as:

1. Always start with `kidney` (the series anchor).
2. Then add **3–6 topic tags** capturing this issue's PRINCIPAL themes — the same
   themes you name in the Overview, **not** every paper's sub-topic.

Choose those topic tags **only** from this closed vocabulary, copied **verbatim**
(exact spelling, all lowercase, singular, no `&`):

`immunosuppression` · `rejection` · `tolerance` · `infection` · `cardiometabolic` ·
`pharmacology` · `biomarkers` · `AI / machine learning` · `donor utilisation` ·
`living donation` · `machine perfusion` · `desensitisation` · `perioperative` ·
`graft survival` · `access` · `health economics` · `paediatric`

Rules:
- Tag only the issue's headline themes (3–6). Tagging every sub-topic makes the filter
  meaningless once there are dozens of issues; the value is in the rarer, specific tags.
- Every topic tag must correspond to a theme you actually named in the Overview.
- Use the strings EXACTLY as listed — do not pluralise, rephrase, or invent. If a
  relevant theme is not on the list, leave it untagged rather than coin a new tag.
- Never use `weekly briefing` or any free-form keyword.

Body (in this exact order):

````
::: {.callout-note appearance="simple"}
AI-generated summary. Verify each item against the source before relying on it.
:::

::: {.kw-overview}
A 4–6 sentence thematic synthesis of this issue's papers: name the main
themes (e.g. immunosuppression minimisation, donor utilisation/DCD, rejection biomarkers,
cardiovascular risk, infection prevention) and weave the selected papers together by
theme rather than listing them. Do NOT begin with a literal "Overview." label — the site
adds a styled "In brief" eyebrow automatically. If no full texts were available this run,
end with: "Note: no full texts were available via PubMed Central for the selected papers
in this run, so every summary below is grounded strictly in the PubMed abstract."
:::

---

### 1. [Exact article title, verbatim from PubMed](https://doi.org/DOI)
[Full author list. *Journal abbreviation*, YEAR. PMID: PMID.]{.kw-ref}

A 6–10 sentence summary in your own words: the study design and population/setting; the
databases and date range searched and the sample size where given; the main findings
**with specific numbers** — effect sizes, confidence intervals, percentages, I²,
follow-up duration; and any important caveats. Close with one sentence on the implication
for UK kidney transplant practice, woven into the prose (not a separate labelled line).

### 2. [Next article title, verbatim](https://doi.org/DOI)
[Full author list. *Journal abbreviation*, YEAR. PMID: PMID.]{.kw-ref}

Summary as above.

---

*Generated DATE from PubMed search results for kidney transplantation published START to
END. Articles already recorded in prior issues were excluded. PubMed is the source of all
metadata and abstracts.*
````

Notes on layout (match exactly):

- Wrap the Overview in a `::: {.kw-overview}` … `:::` fenced div, and put each reference
  line in a `[ … ]{.kw-ref}` span (no literal "Overview." or "Reference:" labels). These
  two classes drive the site's typography — the Overview renders as a serif lead with an
  "In brief" eyebrow, the reference as small muted print — so keep them exactly.
- A single `---` rule separates the Overview from the numbered entries, and a single `---`
  separates the last entry from the footer. Do **not** put `---` rules between consecutive
  entries — each new entry begins with its `### N.` heading.
- Number entries sequentially. Order them so related papers sit together, loosely
  following the themes named in the Overview.
- If a paper has no DOI, link the title to `https://pubmed.ncbi.nlm.nih.gov/PMID/` instead.

## Step 8 — Update dedup state

- Add the PMIDs you included this run to the `seen` array in `briefings/_state/seen.json`.
  Keep it valid JSON and keep all existing PMIDs. Do not remove anything.

## Step 9 — Open a pull request (never push to main)

- Create a branch named `briefing/DATE`.
- Stage ONLY the `briefings/` directory (the new post and the updated `seen.json`). Do not
  touch any other files. Do not render Quarto — the site's publish workflow renders on
  merge.
- Commit with message `Kidney Watch: DATE`.
- Push the branch and open a pull request targeting `main`, using `gh pr create` if
  available (otherwise the GitHub API). PR title: `Kidney Watch: LONGDATE`. PR body: a
  short bullet list of the included papers (title — PMID).
- Report the pull request URL.

Never push directly to `main`. Never modify files outside the `briefings/` directory.

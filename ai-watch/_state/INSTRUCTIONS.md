# AI in Medicine Watch — generation instructions

You are generating the fortnightly **AI in Medicine Watch** digest for the Quarto site
repository you have checked out. Produce ONE new digest as a Quarto `.qmd` file and open a
pull request. Use **only** the PubMed and Scholar-Gateway connectors for evidence. Work
carefully. Do not fabricate anything. Follow these instructions exactly.

**Scope:** artificial intelligence in clinical medicine — machine learning, deep learning,
large language models and AI-enabled devices **evaluated in patients, clinicians or
clinical data**. Not pure methods papers with no clinical evaluation, not bioinformatics
pipelines, not opinion pieces without new evidence (major guidance and regulatory
statements are the exception — see Step 3).
**Audience:** UK NHS clinicians who use or are being asked to adopt AI tools, and clinical
researchers who build them.
**Cadence and window:** run every two weeks; search articles published in the **last 21
days** (a deliberate ~1-week overlap with the previous issue so late-indexed papers are
not missed; the dedup in Step 1 guarantees nothing already covered is repeated).

---

## Step 1 — Load what has already been covered

- Read `ai-watch/_state/seen.json`. It is JSON of the form `{"seen": ["PMID", ...]}`.
- Collect every PMID in the `seen` array into an exclusion set.
- If the file is missing or the array is empty, the exclusion set is empty.

## Step 2 — Find recent papers

Let `START` = today minus 21 days and `END` = today, both as `YYYY/MM/DD`. **Always pass
both `date_from` and `date_to`** to the PubMed search — a `date_from` on its own is
silently ignored and returns the journal's entire back catalogue.

Run these searches (publication date, `pdat`), retrieving enough results to see every
hit in the window:

1. **Dedicated AI journals — everything they publish in the window:**
   `"NEJM AI"[Journal] OR "Lancet Digit Health"[Journal] OR "NPJ Digit Med"[Journal]`

2. **High-impact general and specialty journals — AI papers only:**
   `("N Engl J Med"[Journal] OR "Lancet"[Journal] OR "JAMA"[Journal] OR "BMJ"[Journal]
   OR "Nat Med"[Journal] OR "Nature"[Journal] OR "JAMA Netw Open"[Journal]
   OR "JAMA Intern Med"[Journal] OR "JAMA Surg"[Journal] OR "Ann Intern Med"[Journal])
   AND AI_FILTER`

   JAMA's AI content (the curated JAMA+ AI channel) is published in JAMA and the JAMA
   Network journals, so it is covered here.

3. **Transplantation and nephrology — AI papers only** (the series' home specialty; a
   strong paper here is worth a place even if it would not otherwise make the cut):
   `("Am J Transplant"[Journal] OR "Transplantation"[Journal] OR "Kidney Int"[Journal]
   OR "J Am Soc Nephrol"[Journal] OR "Transpl Int"[Journal]) AND AI_FILTER`

where `AI_FILTER` is:

`("Artificial Intelligence"[MeSH Terms] OR "Machine Learning"[MeSH Terms]
OR "artificial intelligence"[Title/Abstract] OR "machine learning"[Title/Abstract]
OR "deep learning"[Title/Abstract] OR "large language model"[Title/Abstract]
OR "large language models"[Title/Abstract] OR "neural network"[Title/Abstract])`

For each candidate, retrieve full metadata **and** the abstract (PMID, title, full author
list, journal, year, DOI, abstract, publication type). Discard any article whose PMID is
in the exclusion set, and anything that is an erratum, a reply, or has no abstract.

## Step 3 — Select the most significant

From the remaining NEW articles, read the abstracts and select **up to 8**, judged by how
much they should change what a UK clinician believes or does about clinical AI.
Prioritise, roughly in this order:

1. Randomised or prospective evaluations of an AI tool in real clinical care, with
   patient or workflow outcomes.
2. External validation or real-world deployment studies (multi-site, different country or
   population, silent-mode trials, post-deployment monitoring) — including evidence that
   a tool **did not** perform.
3. Rigorous evaluations of large language models on clinical tasks, especially against
   clinicians and with safety or error analysis.
4. Reporting guidelines, consensus statements, and regulatory or governance guidance
   (e.g. TRIPOD+AI, CONSORT-AI, MHRA, NICE, FDA, WHO) published in the window.
5. Large systematic reviews or meta-analyses of clinical AI.

Aim for breadth: avoid more than three papers from one clinical specialty or one journal
unless the window genuinely demands it. Include at least one transplantation or
nephrology paper if a search-3 result meets the bar — never force one in.

Only consider articles actually returned by THIS run's PubMed searches. Never add papers
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
- Report performance metrics exactly as the source gives them (AUROC, sensitivity,
  specificity, PPV, calibration, accuracy) and say **what** they were measured against —
  the reference standard, the comparator (clinicians, existing score, usual care), and
  whether the test set was internal or external. A metric with no comparator is not a
  finding.
- Name the AI system or model as the source names it (including model version where
  given). Do not add vendor claims or model details from outside the source.
- If you are unsure any detail is correct, **OMIT that paper** rather than guess.

## Step 6 — Empty-window guard

- If, after deduplication, there are ZERO new notable items, do **not** create a post,
  commit, or open a PR. Report "No new notable items this fortnight" and stop.

## Step 7 — Write the digest (follow this format EXACTLY)

- Use today's UTC date. Let `DATE` = `YYYY-MM-DD`, `LONGDATE` = e.g. `21 June 2026`,
  `START` = `DATE` minus 21 days, `END` = `DATE`.
- Create `ai-watch/DATE/index.qmd`. The Quarto front-matter `title` becomes the page H1,
  so the body must **not** repeat a top-level (`#`) heading.

Front matter:

```
---
title: "AI in Medicine Watch: LONGDATE"
date: "DATE"
categories: [<3–6 topic tags from the closed vocabulary below>]
description: "One-line summary of this issue's notable clinical AI literature."
---
```

### Topic tags (`categories`) — choose from a CLOSED vocabulary

The front-matter `categories` powers the reader's topic filter on the listing page, so
the strings must be **identical across issues** or the filter fragments into useless
singletons. Add **3–6 topic tags** capturing this issue's PRINCIPAL themes — the same
themes you name in the Overview, **not** every paper's sub-topic.

Choose them **only** from this closed vocabulary, copied **verbatim** (exact spelling,
all lowercase, singular, no `&`):

`large language models` · `medical imaging` · `clinical decision support` ·
`prediction models` · `ambient documentation` · `diagnostics` · `trials` ·
`external validation` · `bias and equity` · `safety` · `regulation` · `governance` ·
`reporting standards` · `education` · `transplantation` · `surgery`

Rules:
- Tag only the issue's headline themes (3–6). Tagging every sub-topic makes the filter
  meaningless once there are dozens of issues.
- Every topic tag must correspond to a theme you actually named in the Overview.
- Use the strings EXACTLY as listed — do not pluralise, rephrase, or invent. If a
  relevant theme is not on the list, leave it untagged rather than coin a new tag.

Body (in this exact order):

````
::: {.callout-note appearance="simple"}
AI-generated summary. Verify each item against the source before relying on it.
:::

::: {.kw-overview}
A 4–6 sentence thematic synthesis of this issue's papers: name the main themes (e.g.
prospective LLM evaluation, external validation failures, imaging AI in screening,
regulation) and weave the selected papers together by theme rather than listing them.
Where the evidence is mixed — a tool that worked in development but not on external
data — say so plainly. Do NOT begin with a literal "Overview." label — the site adds a
styled "In brief" eyebrow automatically. If no full texts were available this run, end
with: "Note: no full texts were available via PubMed Central for the selected papers in
this run, so every summary below is grounded strictly in the PubMed abstract."
:::

---

### 1. [Exact article title, verbatim from PubMed](https://doi.org/DOI)
[Full author list. *Journal abbreviation*, YEAR. PMID: PMID.]{.kw-ref}

A 6–10 sentence summary in your own words: the study design, setting and population;
what the AI system was, what it was compared against and the reference standard; the
sample size and whether evaluation was internal, external or prospective; the main
findings **with specific numbers** — effect sizes, AUROC, sensitivity/specificity,
confidence intervals, error rates; and the important caveats (single site, retrospective
data, spectrum bias, no patient outcomes). Close with one sentence on what it means for a
UK clinician deciding whether to trust or adopt a tool like this, woven into the prose
(not a separate labelled line).

### 2. [Next article title, verbatim](https://doi.org/DOI)
[Full author list. *Journal abbreviation*, YEAR. PMID: PMID.]{.kw-ref}

Summary as above.

---

*Generated DATE from PubMed search results for clinical AI published START to END in
dedicated AI journals, high-impact general journals, and transplantation and nephrology
journals. Articles already recorded in prior issues were excluded. PubMed is the source
of all metadata and abstracts.*

*How this digest is made: [From a literature-search skill to a self-running evidence digest](/posts/automated-literature-watch/).*

## More issues {.unlisted}

:::{#previous-issues}
:::
````

Notes on layout (match exactly):

- Wrap the Overview in a `::: {.kw-overview}` … `:::` fenced div, and put each reference
  line in a `[ … ]{.kw-ref}` span (no literal "Overview." or "Reference:" labels). These
  classes are shared with Kidney Watch and drive the site's typography.
- A single `---` rule separates the Overview from the numbered entries, and a single `---`
  separates the last entry from the footer. Do **not** put `---` rules between consecutive
  entries — each new entry begins with its `### N.` heading.
- Number entries sequentially. Order them so related papers sit together, loosely
  following the themes named in the Overview.
- If a paper has no DOI, link the title to `https://pubmed.ncbi.nlm.nih.gov/PMID/` instead.

## Step 8 — Update dedup state

- Add the PMIDs you included this run to the `seen` array in `ai-watch/_state/seen.json`.
  Keep it valid JSON and keep all existing PMIDs. Do not remove anything.

## Step 9 — Open a pull request (never push to main)

- Create a branch named `ai-watch/DATE`.
- Stage ONLY the `ai-watch/` directory (the new post and the updated `seen.json`). Do not
  touch any other files. Do not render Quarto — the site's publish workflow renders on
  merge.
- Commit with message `AI in Medicine Watch: DATE`.
- Push the branch and open a pull request targeting `main`, using `gh pr create` if
  available (otherwise the GitHub API). PR title: `AI in Medicine Watch: LONGDATE`. PR
  body: a short bullet list of the included papers (title — journal — PMID).
- Report the pull request URL.

Never push directly to `main`. Never modify files outside the `ai-watch/` directory.

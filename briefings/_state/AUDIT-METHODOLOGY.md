# Kidney Watch — audit methodology

A reusable checklist for periodically auditing the Kidney Watch pipeline: does it still
comply with its own spec (`briefings/_state/INSTRUCTIONS.md`), are its citations still
accurate against live PubMed, and is it sourcing from the journals it should be? Written so
a fresh Claude session with no memory of any prior audit can run this end to end. First run:
28 August 2026, after 11 issues. Re-run roughly every 10 weeks (see the scheduled trigger
"Kidney Watch 10-week re-audit" in this account's Routines).

**Scope each run to what's new**: only fully re-verify issues published since the last
audit's cutoff date (check `date-modified` in the most recent `posts/evaluating-*` audit
post, or ask the user) — re-running the full 88-citation check every time is wasted effort
once there's a prior clean result on record. Still re-run the cross-issue checks (dedup
bijection, category tally, journal tally, Tier-1 capture rate) across **all** issues,
since those are cheap and only meaningful in aggregate.

## Prerequisites

- Read `briefings/_state/INSTRUCTIONS.md` in full — it is the ground truth to audit
  against, not external literature-review standards, and it changes over time (e.g. as of
  28 Aug 2026 it added Scholar Gateway as a real secondary search channel, with a
  documented corpus-staleness caveat — check for further changes since).
- Tools needed: `mcp__PubMed__*` (citation verification), `mcp__github__*` (PR history,
  optional), Bash/Python (structural parsing), WebSearch (SCImago/SJR lookups).

## Step 1 — Structural / spec-compliance sweep (all issues, no PubMed calls)

Parse every `briefings/????-??-??/index.qmd` programmatically (Python, not manual reading)
and check: front matter `categories` starts with `kidney`, every other tag is verbatim from
the closed vocabulary in `INSTRUCTIONS.md` Step 7, tag count is 3–6; exactly 8 numbered
entries (`### N.`) and 8 `.kw-ref` spans; required sections present (`.callout-note`,
`.kw-overview`, `## More issues`, `{#previous-issues}`); footer wording matches the current
spec's template.

**Known pitfall (hit on the first audit, 28 Aug 2026)**: a naive per-line regex parser will
mis-parse an entry whose DOI contains an embedded parenthesis (e.g.
`10.1016/S0140-6736(26)00718-X` — real, valid, Lancet-style) and silently drop that entry,
producing a false "missing entry" / false "orphaned PMID" finding. Parse each numbered entry
as a **block** (split on `### N.` boundaries first), not with one link-matching regex that
assumes no nested parentheses in the URL. Verify a "compliance error" is real by opening the
actual file before reporting it — a bug in your own parser is more likely than 11-for-11
issues suddenly breaking the same way at once.

## Step 2 — Dedup / window integrity (all issues)

Extract every cited PMID from every issue; confirm it's an exact bijection against
`briefings/_state/seen.json` (nothing cited-but-unlogged, nothing logged-but-uncited, no
duplicates in either set). Extract each issue's footer window (`published START to END`);
confirm no real gaps — note that consecutive windows are *supposed* to overlap (14-day
window, ~7-day cadence), so "prev.END != cur.START" is expected, not a bug. The real check
is `prev.END >= cur.START` (no gap) plus a sanity check that the overlap is consistently
~7 days (wider only around known bootstrap/correction periods).

## Step 3 — Citation accuracy (the core check)

Batch-verify **every** PMID in `seen.json` against live PubMed — this is cheap enough to do
exhaustively, not by sampling. `mcp__PubMed__get_article_metadata` caps at **20 PMIDs per
call**; chunk accordingly and check each response's actual count rather than assuming 20
always returns. Large batches get redirected to a file — process with Python/jq, don't Read
the raw dump (abstracts/MeSH bloat the payload ~10x beyond what's needed).

For each paper, diff the published `.qmd` text against PubMed's record on: title (normalize
only a trailing-period difference — Kidney Watch drops it, PubMed keeps it; that's cosmetic,
not a discrepancy), DOI, journal abbreviation, year, and the full author sequence
(reconstruct from PubMed's `last_name`+`initials` fields and compare surname-by-surname, not
just author count). Name every real discrepancy specifically (PMID, field,
published-vs-actual) rather than reporting a bare pass/fail rate.

**Mandatory**: PubMed's own usage terms require "According to PubMed" attribution and a DOI
link wherever its data is used to state a fact — carry this into the report/dashboard.

## Step 4 — Scope adherence

Grep all entries' titles for multi-organ/combined-transplant signals (`pancreas`,
`heart-kidney`, `liver-kidney`, `bladder-kidney`, `multivisceral`, `simultaneous`, etc.).
As of 28 Aug 2026 the spec explicitly allows combined-organ transplants where kidney is a
co-primary outcome (only pancreas stays excluded) — check new entries against that rule,
not against a stricter "kidney-only" reading.

## Step 5 — Journal sourcing & scientometric quality

- Tally journal frequency across all entries (regex the `*Journal*,` field from each
  `.kw-ref` line).
- Tier-1 reference set: American Journal of Transplantation, Transplantation, Kidney
  International, JASN, CJASN, AJKD, Nephrology Dialysis Transplantation, Transplant
  International, NEJM, JAMA, The Lancet. For each, run one `mcp__PubMed__search_articles`
  query (`"<Journal>"[Journal] AND kidney transplantation`) over the aggregate window since
  the last audit, to get its true candidate pool; diff against `seen.json` for a per-journal
  and overall capture rate. A low-but-nonzero rate is normal (the pipeline picks ≤8/week
  from every journal combined, not a per-journal quota) — a **zero** rate on a journal with
  a real candidate pool is the signal worth chasing: batch-fetch `article_types` for its
  not-selected candidates and check whether any look like an obvious pass-over (RCT/large
  registry/guideline) versus what was actually selected that period.
- SJR/quartile: `scimagojr.com` blocks direct WebFetch (403) — use WebSearch instead
  (e.g. `"<Journal>" SCImago SJR quartile`), which reliably surfaces the figures from
  indexed pages. True Journal Impact Factor (Clarivate JCR) is paywalled; SJR is the
  practical free substitute.
- Evidence-hierarchy tally: use the `article_types` field already pulled in Step 3 (no
  extra PubMed calls) to classify selected papers (RCT / meta-analysis / systematic review
  / guideline / etc.). Caveat this explicitly: PubMed doesn't tag "registry study" or
  "cohort study" as a distinct type, so large OPTN/UNOS/SRTR-scale analyses — exactly what
  the spec prioritises — mostly show up only as plain "Journal Article." Don't let this
  chart imply low quality; it undercounts registry/cohort evidence structurally.
- Citation counts are not a usable metric for papers this fresh (most are under 14 weeks
  old) and the connected PubMed tools don't expose a cited-by field anyway — state this
  limitation rather than reporting a near-uniform zero as if it meant something.

## Step 6 — Process context (one paragraph, not its own workstream)

Pull PR history for issues since the last audit (`mcp__github__search_pull_requests`,
query `Kidney Watch in:title`) — cadence, review-comment count, anything caught pre-merge.
Cross-check `INSTRUCTIONS.md` for internal consistency (e.g. does the opening connector
line match what Steps 2–3 actually instruct?) and cross-check that
`posts/automated-literature-watch/index.qmd`'s claims about the pipeline still match
`INSTRUCTIONS.md`'s actual current behavior — they're meant to stay in sync, and prior
audits have found them drift apart (Aug 2026: the post described PubMed-only search after
Scholar Gateway was added to the routine's live connector list but not yet wired into the
spec's search steps).

## Output

- **Chat summary**: headline verdict (N/N issues compliant, dedup bijection status, N/N
  citations verified with results), anything requiring the user's judgment (a scope
  question, a sourcing gap) called out explicitly, link to the dashboard.
- **Artifact (HTML dashboard)**: citation-accuracy scorecard, category/topic distribution,
  issue timeline, journal distribution with Tier-1 highlighted, Tier-1 capture-rate table,
  evidence-hierarchy breakdown. Load the `artifact-design` and `dataviz` skills before
  building it. **Render it and look at it** (headless Chromium is pre-installed at
  `/opt/pw-browsers/chromium-*/chrome-linux/chrome`; a global `playwright` npm package is
  installed — set `NODE_PATH=$(npm root -g)` to reach it from a script) — check light mode,
  dark mode, and a narrow viewport for overflow before publishing.
- Findings and fixes from each run should feed a short follow-up to the
  `posts/evaluating-*` blog post lineage if the findings are substantive enough to write up
  (see the 28 Aug 2026 post for the pattern) — not every run needs a new post, but a
  material spec change or a newly-found systematic issue is worth documenting publicly,
  matching this project's own transparency principle.

## What's already been fixed (don't re-flag these)

- Multi-organ combined-transplant scope: resolved 28 Aug 2026 (see Step 4).
- "et al." truncation and compound-surname author-list bugs: spec rule added 28 Aug 2026
  (`INSTRUCTIONS.md` Step 5) — check whether it's actually holding in issues published since.
- Scholar Gateway wired into real search (not just named but unused): resolved 28 Aug 2026
  — check whether its yield has improved as its corpus freshness catches up (it was ~4
  months stale at integration time), and whether the DOI-extraction-from-`link`/
  `citationLine` approach is still needed (check if Scholar Gateway's schema has since
  added a dedicated `doi` field).

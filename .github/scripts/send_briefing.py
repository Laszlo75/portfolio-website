#!/usr/bin/env python3
"""Email one Kidney Watch or AI in Medicine Watch issue via the Buttondown API.

Called from .github/workflows/publish.yml after a new briefings/<date>/index.qmd
or ai-watch/<date>/index.qmd is published. Reads the freshly rendered feed
(_site/briefings.xml or _site/ai-watch.xml; feed: type: full, so each item
carries the whole issue), finds the item for the given date, and schedules it as
a Buttondown email a few minutes out.

Both newsletters share one Buttondown account. Subscribers are told apart by the
tag their signup form adds ("kidney-watch" / "ai-watch"), and each email carries
a recipient filter so a list only ever gets its own newsletter:
  - AI in Medicine Watch goes only to subscribers tagged "ai-watch".
  - Kidney Watch goes to subscribers tagged "kidney-watch" OR not tagged
    "ai-watch" — the second clause keeps everyone who signed up before tagging
    existed, so no existing subscriber is dropped.

Scheduling (status="scheduled" + publish_date) is on Buttondown's free plan and
does not require the "live dangerously" send header. Stdlib only — no deps.

Usage: python3 send_briefing.py <YYYY-MM-DD> [--series kidney|ai] [--draft]
       --series defaults to kidney.
       --draft posts the email as a Buttondown draft instead of scheduling it,
       so it never reaches subscribers — open it in the dashboard and use
       "Send test email" to check rendering in real inboxes.
Env:   BUTTONDOWN_API_KEY (required to send; absent = no-op)
"""

import datetime
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from defusedxml.ElementTree import parse as parse_xml  # XXE/entity-safe XML parsing

API_URL = "https://api.buttondown.com/v1/emails"
TAGS_URL = "https://api.buttondown.com/v1/tags"
SEND_DELAY_MIN = 5  # schedule slightly ahead so the deployed page is live by send time

KIDNEY_TAG = "kidney-watch"
AI_TAG = "ai-watch"

SERIES = {
    "kidney": {
        "feed": "_site/briefings.xml",
        "path": "briefings",
        "name": "Kidney Watch",
        "masthead": "Kidney Transplant Watch",
        "strapline": "A weekly watch on new kidney transplantation literature",
    },
    "ai": {
        "feed": "_site/ai-watch.xml",
        "path": "ai-watch",
        "name": "AI in Medicine Watch",
        "masthead": "AI in Medicine Watch",
        "strapline": "A fortnightly watch on clinical AI research",
    },
}

# Mirrors the teal/navy palette and type scale in styles.css. Re-declared here
# (rather than linked) because email clients never fetch the site stylesheet —
# without this, Quarto's kw-overview/kw-ref/callout classes render unstyled.
EMAIL_STYLE = """
<style>
  .kw-email h1, .kw-email h2, .kw-email h3 {
    font-family: Georgia, 'Times New Roman', serif;
    color: #1a2332;
    line-height: 1.3;
  }
  .kw-email h3 { font-size: 1.15rem; margin: 1.9rem 0 0.5rem; }
  .kw-email h3 a { color: #1a2332; text-decoration: none; }
  .kw-email p { margin: 0 0 1rem; line-height: 1.65; }
  .kw-email a { color: #1a7a8a; }
  .kw-email hr { border: none; border-top: 1px solid #e2e5ea; margin: 1.75rem 0; }
  .kw-email .kw-overview {
    font-family: Georgia, serif;
    font-size: 1.1rem;
    line-height: 1.6;
    color: #1a2332;
    border-left: 3px solid #1a7a8a;
    padding: 0.1rem 0 0.1rem 1.1rem;
    margin: 0 0 1.75rem;
  }
  .kw-email .kw-overview::before {
    content: "In brief";
    display: block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #1a7a8a;
    margin-bottom: 0.4rem;
  }
  .kw-email .kw-ref {
    display: block;
    font-size: 0.82rem;
    line-height: 1.45;
    color: #6b7280;
    margin: 0.15rem 0 0.9rem;
  }
  .kw-email .kw-ref a { color: #1a7a8a; }
  .kw-email .callout {
    border-left: 3px solid #1a7a8a;
    background: #f2f8f9;
    border-radius: 0 6px 6px 0;
    padding: 0.9rem 1.1rem;
    margin: 0 0 1.75rem;
  }
  .kw-email .callout p { margin: 0; font-size: 0.92rem; color: #374151; }
  .kw-email .callout-icon-container,
  .kw-email .callout-title-container { display: none; }
  .kw-email .quarto-listing,
  .kw-email #previous-issues,
  .kw-email #more-issues { display: none; }
</style>
"""


def absolutize_links(html: str, base: str) -> str:
    """Rewrite relative href/src URLs to absolute against the issue's URL.

    Quarto's feed makes image src absolute but leaves <a href> relative (e.g.
    the "More issues" list and cross-post links render as ../../...), which
    breaks once the HTML is lifted into an email client. Resolve them so every
    internal link points at the live site.
    """

    def repl(m: "re.Match[str]") -> str:
        attr, url = m.group(1), m.group(2)
        if url[:1] == "#" or url.split(":", 1)[0] in ("mailto", "tel", "data"):
            return m.group(0)
        return f'{attr}="{urllib.parse.urljoin(base, url)}"'

    return re.sub(r'(href|src)="([^"]+)"', repl, html)


def strip_more_issues(content: str) -> str:
    """Drop the "More issues" heading and its previous-issues listing entirely.

    CSS alone (display:none) isn't enough — Outlook's Word rendering engine
    ignores embedded <style> blocks, so the heading and unstyled listing cards
    reappeared there even though EMAIL_STYLE hides them. This section is
    always the last thing in a rendered briefing (see briefings/_metadata.yml),
    so cutting from the heading onward removes it for every client.
    """
    return re.sub(
        r'<h2[^>]*\bid=["\']more-issues["\'][^>]*>.*',
        "",
        content,
        flags=re.S,
    )


def tag_ids(api_key: str) -> dict:
    """Map tag name -> Buttondown tag id (email filters take ids, not names)."""
    ids, url = {}, TAGS_URL
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Token {api_key}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            page = json.loads(resp.read().decode())
        ids.update({t["name"]: t["id"] for t in page.get("results", [])})
        url = page.get("next")
    return ids


def recipient_filter(series: str, ids: dict):
    """Buttondown filter limiting an email to its own newsletter's subscribers.

    Returns None to send to everyone. Raises if the AI list can't be targeted —
    better to skip a send than email the AI digest to the whole Kidney Watch list.
    """

    def has(tag, op="contains"):
        return {"field": "subscriber.tags", "operator": op, "value": ids[tag]}

    if series == "ai":
        if AI_TAG not in ids:
            raise RuntimeError(f"Buttondown tag '{AI_TAG}' not found — refusing to send to all.")
        return {"predicate": "and", "groups": [], "filters": [has(AI_TAG)]}

    if AI_TAG not in ids:
        return None  # nobody has signed up for AI Watch yet, so everyone is Kidney Watch
    clauses = [has(AI_TAG, "not_contains")]
    if KIDNEY_TAG in ids:
        clauses.append(has(KIDNEY_TAG))
    return {"predicate": "or", "groups": [], "filters": clauses}


def main() -> int:
    args = sys.argv[1:]
    draft = "--draft" in args
    args = [a for a in args if a != "--draft"]
    series = "kidney"
    if "--series" in args:
        i = args.index("--series")
        series = args[i + 1] if i + 1 < len(args) else ""
        del args[i : i + 2]
    if len(args) < 1 or series not in SERIES:
        print(
            "Usage: send_briefing.py <YYYY-MM-DD> [--series kidney|ai] [--draft]",
            file=sys.stderr,
        )
        return 2
    issue_date = args[0]
    cfg = SERIES[series]
    feed_path = cfg["feed"]

    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key:
        print("BUTTONDOWN_API_KEY not set — skipping send.")
        return 0

    try:
        items = parse_xml(feed_path).getroot().findall(".//item")
    except Exception as exc:  # parse / IO / defused-entity errors — log and bail
        print(f"Could not read {feed_path}: {exc}", file=sys.stderr)
        return 1

    if not items:
        print("Feed has no items — nothing to send.")
        return 0

    # Match the item whose link points at this issue's date; fall back to newest.
    target = next(
        (it for it in items if f"/{cfg['path']}/{issue_date}/" in (it.findtext("link") or "")),
        items[0],
    )

    subject = target.findtext("title") or f"{cfg['name']}: {issue_date}"
    link = target.findtext("link") or f"https://lszabo.me/{cfg['path']}/"
    content = target.findtext("description") or ""
    if not content.strip():
        print("Issue content is empty — skipping send.", file=sys.stderr)
        return 1

    content = absolutize_links(content, link)  # internal links must work in email
    content = strip_more_issues(content)  # unstyled listing cruft, not worth emailing

    body = f"""\
{EMAIL_STYLE}
<div class="kw-email" style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#374151;max-width:640px;margin:0 auto;">
  <div style="background:#1a2332;border-radius:8px 8px 0 0;padding:26px 32px;text-align:center;">
    <div style="font-family:Georgia,serif;color:#ffffff;font-size:21px;font-weight:600;">{cfg['masthead']}</div>
    <div style="color:#b9c6d0;font-size:13px;margin-top:4px;">{cfg['strapline']}</div>
  </div>
  <div style="background:#ffffff;border:1px solid #e2e5ea;border-top:none;border-radius:0 0 8px 8px;padding:28px 32px;">
    <h1 style="font-family:Georgia,serif;color:#1a2332;font-size:1.4rem;margin:0 0 1rem;">{html.escape(subject)}</h1>
    <p style="margin:0 0 1.5rem;">
      <a href="{link}" style="color:#1a7a8a;font-weight:600;text-decoration:none;">Read this issue on lszabo.me &rarr;</a>
      — best for the full, styled version.
    </p>
    {content}
    <hr style="border:none;border-top:1px solid #e2e5ea;margin:1.75rem 0 1rem;">
    <p style="font-size:0.8rem;color:#9ca3af;margin:0;">
      {cfg['name']} summaries are AI-generated from PubMed and reviewed before publishing — always verify against the primary source.
    </p>
  </div>
</div>
"""

    if draft:
        payload = {"subject": subject, "body": body, "status": "draft"}
    else:
        publish_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=SEND_DELAY_MIN
        )
        payload = {
            "subject": subject,
            "body": body,
            "status": "scheduled",
            "publish_date": publish_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    try:
        filters = recipient_filter(series, tag_ids(api_key))
    except (urllib.error.URLError, RuntimeError, KeyError, ValueError) as exc:
        print(f"Could not resolve recipient tags — not sending: {exc}", file=sys.stderr)
        return 1
    if filters:
        payload["filters"] = filters

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            out = json.loads(resp.read().decode())
        if draft:
            print(
                f"Created draft '{subject}' (id {out.get('id')}) — open it in the "
                "Buttondown dashboard and use \"Send test email\" to check rendering."
            )
        else:
            print(
                f"Scheduled '{subject}' (id {out.get('id')}) for "
                f"{out.get('publish_date')} — status {out.get('status')}."
            )
        return 0
    except urllib.error.HTTPError as exc:
        print(f"Buttondown API error {exc.code}: {exc.read().decode()[:500]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Buttondown request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

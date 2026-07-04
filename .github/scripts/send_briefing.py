#!/usr/bin/env python3
"""Email one Kidney Watch issue to the Buttondown list via the API.

Called from .github/workflows/publish.yml after a new briefings/<date>/index.qmd
is published. Reads the freshly rendered _site/briefings.xml (feed: type: full,
so each item carries the whole issue), finds the item for the given date, and
schedules it as a Buttondown email a few minutes out.

Scheduling (status="scheduled" + publish_date) is on Buttondown's free plan and
does not require the "live dangerously" send header. Stdlib only — no deps.

Usage: python3 send_briefing.py <YYYY-MM-DD> [--draft]
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

FEED_PATH = "_site/briefings.xml"
API_URL = "https://api.buttondown.com/v1/emails"
SEND_DELAY_MIN = 5  # schedule slightly ahead so the deployed page is live by send time

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


def main() -> int:
    args = sys.argv[1:]
    draft = "--draft" in args
    args = [a for a in args if a != "--draft"]
    if len(args) < 1:
        print("Usage: send_briefing.py <YYYY-MM-DD> [--draft]", file=sys.stderr)
        return 2
    issue_date = args[0]

    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key:
        print("BUTTONDOWN_API_KEY not set — skipping send.")
        return 0

    try:
        items = parse_xml(FEED_PATH).getroot().findall(".//item")
    except Exception as exc:  # parse / IO / defused-entity errors — log and bail
        print(f"Could not read {FEED_PATH}: {exc}", file=sys.stderr)
        return 1

    if not items:
        print("Feed has no items — nothing to send.")
        return 0

    # Match the item whose link points at this issue's date; fall back to newest.
    target = next(
        (it for it in items if f"/briefings/{issue_date}/" in (it.findtext("link") or "")),
        items[0],
    )

    subject = target.findtext("title") or f"Kidney Watch: {issue_date}"
    link = target.findtext("link") or "https://lszabo.me/briefings/"
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
    <div style="font-family:Georgia,serif;color:#ffffff;font-size:21px;font-weight:600;">Kidney Transplant Watch</div>
    <div style="color:#b9c6d0;font-size:13px;margin-top:4px;">A weekly watch on new kidney transplantation literature</div>
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
      Kidney Watch summaries are AI-generated from PubMed and reviewed before publishing — always verify against the primary source.
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

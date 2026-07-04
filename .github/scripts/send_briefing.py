#!/usr/bin/env python3
"""Email one Kidney Watch issue to the Buttondown list via the API.

Called from .github/workflows/publish.yml after a new briefings/<date>/index.qmd
is published. Reads the freshly rendered _site/briefings.xml (feed: type: full,
so each item carries the whole issue), finds the item for the given date, and
schedules it as a Buttondown email a few minutes out.

Scheduling (status="scheduled" + publish_date) is on Buttondown's free plan and
does not require the "live dangerously" send header. Stdlib only — no deps.

Usage: python3 send_briefing.py <YYYY-MM-DD>
Env:   BUTTONDOWN_API_KEY (required to send; absent = no-op)
"""

import datetime
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


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py <YYYY-MM-DD>", file=sys.stderr)
        return 2
    issue_date = sys.argv[1]

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

    body = (
        f'<p style="margin:0 0 1.25rem"><a href="{link}">Read this issue on lszabo.me</a> '
        f"— best for the full, styled version.</p>\n" + content
    )

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

#!/usr/bin/env python3
"""Fetch new talks from the ThibeauWouters/slides GitHub repo into _talks/.

Like fetch_inspire_publications.py, this is INCREMENTAL and NON-DESTRUCTIVE:
it only creates new .md files for talk folders (<year>/<slug>/ in the slides
repo) that aren't already linked from an existing _talks/*.md file. It never
edits an existing file. Re-run whenever you add a new talk folder to the
slides repo.

Each talk folder may contain a CLAUDE.md with a metadata header like:

    **Title:** ...
    **Venue:** ...
    **Date:** December 8, 2023

which is used to fill in title/venue/date. `type` and `location` can't be
derived from that file, so they're left as sensible defaults ("Talk" / "") --
review and edit the newly created file(s) by hand afterwards.

Requires the `gh` CLI, already used elsewhere in this repo, authenticated
(`gh auth status`).

Usage:
    python3 markdown_generator/fetch_slides_talks.py [--dry-run]
"""

import argparse
import base64
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = "ThibeauWouters/slides"
TALKS_DIR = Path(__file__).resolve().parent.parent / "_talks"
FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
FOLDER_RE = re.compile(r"^\d{4}/[^/]+$")


def gh_api(path):
    result = subprocess.run(
        ["gh", "api", path], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def list_talk_folders():
    tree = gh_api(f"repos/{REPO}/git/trees/main?recursive=true")
    return sorted(
        entry["path"] for entry in tree["tree"]
        if entry["type"] == "tree" and FOLDER_RE.match(entry["path"])
    )


def existing_links():
    links = set()
    for path in TALKS_DIR.glob("*.md"):
        match = FRONT_MATTER_RE.match(path.read_text())
        if not match:
            continue
        for line in match.group(1).splitlines():
            if line.strip().startswith("link:"):
                if m := re.search(r"['\"]([^'\"]+)['\"]", line):
                    links.add(m.group(1).rstrip("/"))
    return links


def fetch_claude_md(folder):
    try:
        data = gh_api(f"repos/{REPO}/contents/{folder}/CLAUDE.md")
    except subprocess.CalledProcessError:
        return None
    return base64.b64decode(data["content"]).decode("utf-8")


def parse_metadata(claude_md_text, folder):
    slug = folder.split("/", 1)[1]
    title = slug.replace("_", " ").replace("-", " ")
    venue = ""
    date = None

    if claude_md_text:
        if m := re.search(r"\*\*Title:\*\*\s*(.+)", claude_md_text):
            title = m.group(1).strip()
        if m := re.search(r"\*\*Venue:\*\*\s*(.+)", claude_md_text):
            venue = m.group(1).strip()
        if m := re.search(r"\*\*Date:\*\*\s*(.+)", claude_md_text):
            date_str = m.group(1).strip()
            for fmt in ("%B %d, %Y", "%B %Y", "%Y-%m-%d"):
                try:
                    date = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue

    return title, venue, date


def build_entry(folder, title, venue, date):
    slug = folder.split("/", 1)[1]
    file_slug = re.sub(r"[\s_]+", "-", slug).lower()
    file_slug = re.sub(r"[^a-z0-9-]", "", file_slug)
    date = date or datetime.today().strftime("%Y-%m-%d")
    filename = f"{date}-{file_slug}.md"
    permalink = f"/talks/{date}-{file_slug}/"
    link = f"https://github.com/{REPO}/tree/main/{folder}"

    lines = [
        "---",
        f'title: "{title}"',
        "collection: talks",
        'type: "Talk"',
        f"permalink: {permalink}",
        f'venue: "{venue}"',
        f"date: {date}",
        'location: ""',
        f"link: '{link}'",
        "---",
        "",
        f'[Slides on GitHub]({link}){{:target="_blank"}}',
        "",
    ]
    return filename, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                         help="show what would be created without writing files")
    args = parser.parse_args()

    folders = list_talk_folders()
    links = existing_links()

    created = 0
    needs_review = []
    for folder in folders:
        candidate_link = f"https://github.com/{REPO}/tree/main/{folder}"
        if candidate_link.rstrip("/") in links:
            continue

        claude_md = fetch_claude_md(folder)
        title, venue, date = parse_metadata(claude_md, folder)
        filename, content = build_entry(folder, title, venue, date)
        dest = TALKS_DIR / filename
        if dest.exists():
            continue

        if args.dry_run:
            print(f"[dry-run] would create {filename} -- {title[:70]}")
        else:
            dest.write_text(content)
            print(f"created {filename} -- {title[:70]}")
        needs_review.append(filename)
        created += 1

    print(f"\n{created} new talk(s) {'would be ' if args.dry_run else ''}added "
          f"out of {len(folders)} folders found.")
    if needs_review and not args.dry_run:
        print("Review type/location (and venue/date if no CLAUDE.md was found) in:")
        for f in needs_review:
            print(f"  _talks/{f}")


if __name__ == "__main__":
    sys.exit(main())

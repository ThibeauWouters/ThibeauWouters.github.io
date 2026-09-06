#!/usr/bin/env python3
"""Fetch new publications from INSPIRE-HEP into _publications/.

This is INCREMENTAL and NON-DESTRUCTIVE: it only ever creates new .md files
for INSPIRE records that aren't represented yet in _publications/ (matched by
arXiv id, DOI, or a previously-written `inspire_id` field). It never edits or
overwrites an existing file, so any personal notes you've added to a
publication's body are always safe. Re-run it whenever you want to pick up
new papers.

By default, papers tagged with a `collaborations` field (LIGO Scientific /
VIRGO / KAGRA collaboration-wide papers, often with 1000+ authors) are
skipped, since they'd otherwise flood the site with catalog-style entries.
Pass --all to include them too.

Usage:
    python3 markdown_generator/fetch_inspire_publications.py [--all] [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

import requests

AUTHOR_QUERY = "a Wouters, Thibeau"
INSPIRE_API = "https://inspirehep.net/api/literature"
PUBLICATIONS_DIR = Path(__file__).resolve().parent.parent / "_publications"
FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
MAX_SLUG_LEN = 80


def fetch_records(include_collaborations):
    records = []
    page = 1
    while True:
        url = (
            f"{INSPIRE_API}?q={quote(AUTHOR_QUERY)}&sort=mostrecent&size=100"
            f"&page={page}&fields=titles,earliest_date,control_number,"
            f"arxiv_eprints,dois,publication_info,collaborations"
        )
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        hits = resp.json()["hits"]["hits"]
        if not hits:
            break
        for hit in hits:
            meta = hit["metadata"]
            if not include_collaborations and meta.get("collaborations"):
                continue
            records.append(meta)
        if len(hits) < 100:
            break
        page += 1
    return records


def existing_identifiers():
    """Scan _publications/*.md front matter for arXiv ids, DOIs, inspire_ids,
    and title slugs already present, so we never create a duplicate entry
    (the slug fallback matters for records with neither an arXiv id nor a
    DOI, e.g. theses, which INSPIRE still indexes)."""
    arxiv_ids, dois, inspire_ids, slugs = set(), set(), set(), set()
    for path in PUBLICATIONS_DIR.glob("*.md"):
        match = FRONT_MATTER_RE.match(path.read_text())
        if not match:
            continue
        for line in match.group(1).splitlines():
            if m := re.search(r"arxiv\.org/abs/([\w.\-/]+)", line):
                arxiv_ids.add(m.group(1))
            if m := re.search(r"arXiv:([\w.\-/]+)", line):
                arxiv_ids.add(m.group(1))
            if line.strip().startswith("doi:"):
                if m := re.search(r"['\"]([^'\"]+)['\"]", line):
                    dois.add(m.group(1))
            if line.strip().startswith("inspire_id:"):
                if m := re.search(r"(\d+)", line):
                    inspire_ids.add(m.group(1))
            if line.strip().startswith("title:"):
                if m := re.search(r"[\"'](.+)[\"']\s*$", line.strip()):
                    slugs.add(slugify(m.group(1)))
    return arxiv_ids, dois, inspire_ids, slugs


def slugify(title):
    slug = title.replace("{", "").replace("}", "").replace("\\", "")
    slug = re.sub(r"\$[^$]*\$", "", slug)  # drop inline math
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip()).lower()
    slug = re.sub(r"-+", "-", slug)
    return slug[:MAX_SLUG_LEN].rstrip("-")


def normalize_date(date_str):
    if not date_str:
        return "1900-01-01"
    if len(date_str) == 10:
        return date_str
    if len(date_str) == 7:
        return f"{date_str}-01"
    return f"{date_str}-01-01"


def yaml_single_quote(value):
    return "'" + value.replace("'", "''") + "'"


def build_entry(meta):
    title = meta["titles"][0]["title"]
    control_number = str(meta["control_number"])
    arxiv_id = meta.get("arxiv_eprints", [{}])[0].get("value")
    doi = meta.get("dois", [{}])[0].get("value")
    pub_info = (meta.get("publication_info") or [{}])[0]

    if pub_info.get("journal_title") and pub_info.get("journal_volume"):
        venue = f"{pub_info['journal_title']} {pub_info['journal_volume']}"
    elif arxiv_id:
        venue = f"arXiv preprint arXiv:{arxiv_id}"
    else:
        venue = "N/A"

    date = normalize_date(meta.get("earliest_date"))
    slug = slugify(title)
    filename = f"{date}-{slug}.md"
    permalink = f"/publications/{slug}/"
    paperurl = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else (
        f"https://doi.org/{doi}" if doi else None
    )
    inspireurl = f"https://inspirehep.net/literature/{control_number}"

    lines = [
        "---",
        f'title: "{title}"',
        "collection: publications",
        f"permalink: {permalink}",
        f"date: {date}",
        f'venue: "{venue}"',
    ]
    if paperurl:
        lines.append(f"paperurl: {yaml_single_quote(paperurl)}")
    if doi:
        lines.append(f"doi: {yaml_single_quote(doi)}")
    lines.append(f"inspireurl: {yaml_single_quote(inspireurl)}")
    lines.append(f"inspire_id: {control_number}")
    lines.append("---")
    lines.append("")
    if arxiv_id:
        lines.append(f'[Access on arXiv]({paperurl}){{:target="_blank"}}')
        lines.append("")
    if doi:
        lines.append(f'DOI: [{doi}](https://doi.org/{doi}){{:target="_blank"}}')
        lines.append("")

    return filename, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true",
                         help="include collaboration-wide papers")
    parser.add_argument("--dry-run", action="store_true",
                         help="show what would be created without writing files")
    args = parser.parse_args()

    records = fetch_records(include_collaborations=args.all)
    arxiv_ids, dois, inspire_ids, slugs = existing_identifiers()

    created = 0
    for meta in records:
        control_number = str(meta["control_number"])
        arxiv_id = meta.get("arxiv_eprints", [{}])[0].get("value")
        doi = meta.get("dois", [{}])[0].get("value")
        title = meta["titles"][0]["title"]

        if control_number in inspire_ids:
            continue
        if arxiv_id and arxiv_id in arxiv_ids:
            continue
        if doi and doi in dois:
            continue
        if slugify(title) in slugs:
            continue

        filename, content = build_entry(meta)
        dest = PUBLICATIONS_DIR / filename
        if dest.exists():
            continue  # slug collision with an unrelated existing file

        if args.dry_run:
            print(f"[dry-run] would create {filename} -- {title[:70]}")
        else:
            dest.write_text(content)
            print(f"created {filename} -- {title[:70]}")
        created += 1

    print(f"\n{created} new publication(s) {'would be ' if args.dry_run else ''}added "
          f"out of {len(records)} fetched.")


if __name__ == "__main__":
    sys.exit(main())

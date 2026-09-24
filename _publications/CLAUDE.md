# CLAUDE.md — _publications/

Guidance for working with this collection specifically (see the repo-root
`CLAUDE.md` for everything else). This file is excluded from the Jekyll
build (`_publications/CLAUDE.md` is listed under `exclude:` in `_config.yml`)
since it isn't a real publication entry.

## Where publication data comes from

Every entry here corresponds to a record on INSPIRE-HEP
(https://inspirehep.net), found via the author search query `a Wouters,
Thibeau`. The canonical, always-up-to-date list is:

https://inspirehep.net/literature?sort=mostrecent&size=25&page=1&q=find%20a%20thibeau%20wouters%20and%20not%20fa%20abac%20and%20not%20fa%20abbott%20and%20not%20fa%20acernese

(the `not fa ...` clauses drop LIGO/Virgo/KAGRA collaboration-wide papers
whose first author is one of the standard collaboration bylines). That URL
is also linked from `_pages/publications.md` under "Full publication list".

## Front matter fields

- `title`, `collection: publications`, `permalink`, `date`, `venue` — standard.
- `paperurl` — arXiv abstract page (`https://arxiv.org/abs/<id>`), when an
  arXiv id exists. Entries with **no** `paperurl` pointing at `arxiv.org` are
  filtered out of the `/publications/` listing (see below) — this repo only
  displays papers that have an arXiv preprint.
- `doi` — set when INSPIRE has a DOI for the record (often absent for very
  recent preprints).
- `inspireurl` — `https://inspirehep.net/literature/<control_number>`. This
  is what actually gets rendered on the page ("View on INSPIRE-HEP"), via
  `_includes/archive-single.html` and `_layouts/single.html`, which both
  prefer `inspireurl` over the older `citation` field. Publications no
  longer carry a `citation` field for display purposes — don't re-add one;
  look up the INSPIRE record and add `inspireurl`/`inspire_id` instead.
- `inspire_id` — the bare INSPIRE `control_number` (integer), kept alongside
  `inspireurl` so it's easy to re-derive/re-fetch a record without re-parsing
  the URL.
- `inspire_rank` — an integer used purely for display ordering on
  `/publications/` (see below). Lower = more recent. **Not** an INSPIRE
  field — it's assigned locally to match INSPIRE's own `sort=mostrecent`
  ordering, because Jekyll collections don't have a native "match this
  external API's order" sort, and multiple papers sharing the same `date`
  (e.g. two papers both dated the same day) would otherwise sort
  inconsistently (alphabetically by filename) instead of matching INSPIRE.

## How the listing page uses this

`_pages/publications.md` builds the displayed list with:

```liquid
{% assign arxiv_publications = site.publications | where_exp: "post", "post.paperurl contains 'arxiv.org'" | sort: "inspire_rank" %}
{% for post in arxiv_publications %}
  {% include archive-single.html %}
{% endfor %}
```

i.e. arXiv-only, ordered by `inspire_rank` ascending (which mirrors
INSPIRE's `sort=mostrecent`). Entries without an arXiv `paperurl` (e.g. the
Master's thesis) still get their own individual page via the `publications`
collection/permalink, they just don't show up in the `/publications/` list.

## Adding new publications

`markdown_generator/fetch_inspire_publications.py` (documented in the
repo-root CLAUDE.md) creates new files here for INSPIRE records not yet
represented, already setting `inspireurl`/`inspire_id` (no `citation`
field). It does **not** set `inspire_rank` — after running it, re-derive
ranks for the affected papers (script below) or set them by hand so the
listing stays in INSPIRE's `mostrecent` order.

It skips collaboration-wide papers by default (LSC/Virgo/KAGRA papers with
hundreds/thousands of authors); a handful of Virgo-only papers (e.g. design
reports, calibration papers) were added here manually despite carrying a
`collaborations` field on INSPIRE, since they're relevant, focused works
rather than catalog-style collaboration dumps — use judgement, not a strict
rule, when deciding whether to include a flagged collaboration paper.

## Re-deriving `inspireurl` / `inspire_rank` for existing entries

To (re)fetch INSPIRE metadata and rank for the papers already in this
directory (e.g. after adding several new files by hand, or to sanity-check
existing ones), query the same author search used above via the INSPIRE
API and match by arXiv id:

```python
import requests
from urllib.parse import quote

AUTHOR_QUERY = "a Wouters, Thibeau"
url = (f"https://inspirehep.net/api/literature?q={quote(AUTHOR_QUERY)}"
       "&sort=mostrecent&size=100&page=1&fields=titles,control_number,arxiv_eprints,collaborations")
hits = requests.get(url, timeout=30).json()["hits"]["hits"]
# hits[0] is the most recent record; hits[i]["metadata"]["control_number"]
# is the INSPIRE id, arxiv_eprints[0]["value"] the arXiv id.
# inspire_rank = index within this arXiv-only, mostrecent-sorted list (1-based).
```

Paginate (`&page=2`, ...) if there are more than 100 hits. Match existing
`_publications/*.md` files to hits by `paperurl`'s arXiv id, write back
`inspireurl: 'https://inspirehep.net/literature/<control_number>'`,
`inspire_id: <control_number>`, and `inspire_rank: <position in the
arXiv-only mostrecent list>`.

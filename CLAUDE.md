# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is Thibeau Wouters' personal academic website, built on **academicpages** (a fork of the **Minimal Mistakes** Jekyll theme). It is a static site hosted on GitHub Pages at `ThibeauWouters/ThibeauWouters.github.io` (see `repository:` in `_config.yml`). There is no application code to build/test in the software-engineering sense — "development" here means editing Jekyll content (Markdown/YAML) and Sass/JS theme files, then verifying the rendered site locally.

## Commands

Local development (Ruby/Jekyll via Bundler). **Requires Ruby 3.1.x** — the `github-pages` gem pins an old Jekyll (3.9.2) / Liquid (4.0.3) that break on Ruby >= 3.2 (`tainted?`/`untaint` removed) and on Ruby >= 3.3's bundled `logger` gem (`.ruby-version` pins 3.1.7 via rbenv for this reason; don't "fix" this by bumping the Ruby version). Gems are vendored into `vendor/bundle` (gitignored):

```bash
bundle config set --local path 'vendor/bundle'   # once, if not already set
bundle install                                    # install Ruby deps (delete Gemfile.lock and retry on unrelated errors)
bundle exec jekyll build --config _config.yml,_config.dev.yml   # one-off build, output in _site/
bundle exec jekyll serve --config _config.yml,_config.dev.yml   # build + serve at http://localhost:4000, rebuilds on change
bundle exec jekyll serve --config _config.yml,_config.dev.yml --livereload   # same, with browser auto-refresh (native Jekyll flag)
```

Do **not** use `bundle exec jekyll liveserve` (the `hawkins` gem) — see Known failures below.

The `_config.dev.yml` override (disables analytics, sets `url` to localhost) must be layered on top of `_config.yml` for local runs — see Configuration below.

There are no automated tests. "Verifying a change" means building/serving and checking the affected page in a browser, and/or checking the build log for Liquid/YAML errors. Any loose Markdown file at the repo root that isn't meant to become a site page (e.g. this file) must be added to `exclude:` in `_config.yml` — Jekyll Liquid-renders top-level `.md` files even without front matter, so stray `{% ... %}` text (e.g. in a code example) will break the build otherwise.

Frontend asset build (only relevant when touching `assets/js/vendor` or plugins):

```bash
npm run build:js   # concatenates & uglifies vendor JS + _main.js into assets/js/main.min.js
npm run watch:js    # rebuild on change
```

## Content architecture

Jekyll collections drive most of the site; each has its own directory of Markdown files with YAML front matter, and a matching entry in `_config.yml` under `collections:`:

- `_posts/` — blog posts (date-prefixed filenames, standard Jekyll posts).
- `_talks/`, `_publications/`, `_software/` — CV-style collections, each with its own archive page (`_pages/talks.html`, `publications.md`, `software.html`). Front matter fields (e.g. `venue`, `date`, `location`, `paperurl`/`link`, `citation` for publications) are rendered by matching layouts (`_layouts/talk.html`, `_layouts/archive.html`, etc.) and archive-single includes (`_includes/archive-single.html`, `archive-single-talk.html`, `archive-single-talk-cv.html`, ...).
- `_pages/` — standalone pages (e.g. `about.md`, `cv.md`, `gw.md`, `ai-and-ml.md`). Each sets `layout`, `permalink`, and `author_profile` in front matter.
- `_data/navigation.yml` — top nav menu: Publications, Talks, Software, Posts, CV.
- `_data/authors.yml`, `_data/ui-text.yml` — author profile sidebar content and theme UI strings.
- `markdown_generator/` — one-off Jupyter/Python scripts (`pubsFromBib.py`, `publications.py`, `talks.py`) that convert TSV/BibTeX data into pre-formatted Markdown files for `_talks`/`_projects`. Not part of the site build; run manually when bulk-generating new CV entries.
- `markdown_generator/fetch_inspire_publications.py` — fetches new papers from INSPIRE-HEP (author search on "Wouters, Thibeau") and adds them as new files in `_publications/`. Incremental and non-destructive: matches existing files by arXiv id/DOI/title-slug/`inspire_id` and only ever creates files for records not yet present — it never edits an existing file, so personal notes added to a publication's body survive reruns. Skips LVK-collaboration-wide papers (tagged with an INSPIRE `collaborations` field) by default; pass `--all` to include them, `--dry-run` to preview. Run with `python3 markdown_generator/fetch_inspire_publications.py` whenever new papers should be pulled in. Publications no longer carry a `citation` field for display — `_includes/archive-single.html` shows a "View on INSPIRE-HEP" link from the `inspireurl` field instead (older entries without `inspireurl`, e.g. the Master's thesis, still fall back to the old `citation` rendering).
- `markdown_generator/fetch_slides_talks.py` — fetches new talk folders from the `ThibeauWouters/slides` GitHub repo (`<year>/<slug>/`, each with a `CLAUDE.md` metadata header) and adds them as new files in `_talks/`. Same incremental/non-destructive model, matched by the `link` field. Requires the `gh` CLI, authenticated. `type`/`location` can't be derived from the slides repo, so newly created talk files need a manual check/edit after running.

## Layouts and includes

- `_layouts/` defines page shells: `default.html` (base), `single.html` (post/page), `archive.html` (collection listing), `talk.html`, `splash.html`, `compress.html` (minifies final HTML output).
- `_includes/` holds reusable partials pulled in via `{% include %}` — e.g. `head.html`/`head/` for `<head>` assembly, `masthead.html` for the nav bar, `author-profile.html` for the sidebar, `archive-single*.html` for collection item rendering, `comments-providers/` and `analytics-providers/` for pluggable third-party integrations selected via `_config.yml`.
- Sass partials live in `_sass/`, imported by the theme's main stylesheet under `assets/css`; edit the relevant `_sass/_*.scss` partial rather than compiled CSS.

## Configuration

- `_config.yml` is the single source of truth for site metadata, author info, analytics/comments provider selection, collections, and the `repository:` used for GitHub Pages edit links.
- `_config.dev.yml` overrides settings for local dev (disables analytics, sets `url` to localhost, switches Disqus shortname) — this is normally layered in via `--config _config.yml,_config.dev.yml` when serving locally, not used standalone.
- Uploaded static files (PDFs, zips) go under `files/`; they're served at `/files/<name>`.

## Notes

- This repo is meant to stay close to the generic academicpages template so upstream fixes can be pulled in; avoid unnecessary structural changes to theme files (`_layouts`, `_includes`, `_sass`) unless a specific customization is needed for content in `_pages`/`_posts`/`_talks`/etc.
- If Ruby dependency/security warnings appear, deleting `Gemfile.lock` and re-running `bundle install` is the documented fix (per `README.md`).

## Known failures

- **`bundle exec jekyll liveserve` returns a blank page / 500 on every request** (`NoMethodError: undefined method 'key?' for nil:NilClass` in `webrick-1.7.0/.../filehandler.rb`, raised from `jekyll-3.9.2/lib/jekyll/commands/serve/servlet.rb:191` `conditionally_inject_charset`). Cause: the `hawkins` gem (which implements `liveserve`) builds its own WEBrick config in `hawkins-2.0.5/lib/hawkins/liveserve.rb#webrick_opts` and never sets `:MimeTypesCharset`, but Jekyll 3.9.2's servlet unconditionally calls `.key?` on it. This is a `hawkins`/Jekyll version incompatibility, not a content or config bug — it reproduces on a stock checkout with no site content at all. Fix: don't use `jekyll liveserve`; use `jekyll serve --config _config.yml,_config.dev.yml --livereload` instead (Jekyll's own serve command sets `:MimeTypesCharset` correctly and has had built-in livereload support since Jekyll 3.7, making `hawkins` unnecessary). If a `jekyll liveserve` process is already running and serving nothing, kill it (check `lsof -nP -iTCP -sTCP:LISTEN | grep 4000`) and restart with the `--livereload` flag instead.

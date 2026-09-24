# ThibeauWouters.github.io

Personal academic website, built with [Jekyll](https://jekyllrb.com/) on the [academicpages](https://github.com/academicpages/academicpages.github.io) template (a fork of the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme). Deployed automatically via GitHub Pages from the `master` branch — pushing to `master` is all that's needed to publish.

## Build and view locally

This repo requires Ruby **3.1.x** specifically — the `github-pages` gem pins an old Jekyll/Liquid version that breaks on Ruby >= 3.2 (`tainted?`/`untaint` were removed) and on Ruby >= 3.3's bundled `logger` gem. macOS's built-in system Ruby is a different (and much older) version, so it won't work either. Follow all the steps below in order.

### 1. Install rbenv (one-time, per machine)

```bash
brew install rbenv ruby-build
```

`rbenv` lets this project use its own Ruby version without touching your system Ruby.

### 2. Hook rbenv into your shell (one-time, per machine)

Add this line to `~/.zshrc` (or `~/.bashrc` if you use bash):

```bash
eval "$(rbenv init - zsh)"   # use "bash" instead of "zsh" if that's your shell
```

Then restart your terminal (or run `source ~/.zshrc`). Without this step, `ruby`/`gem`/`bundle` silently keep resolving to macOS's system Ruby no matter what this repo's `.ruby-version` file says, and you'll hit errors like `bundler: command not found: jekyll`. Verify it worked:

```bash
type ruby   # should print a path under ~/.rbenv/shims, not /usr/bin/ruby
```

### 3. Install the pinned Ruby version (one-time, per machine)

From inside this repo's directory (so `.ruby-version` is picked up):

```bash
rbenv install 3.1.7   # matches .ruby-version; skips automatically if already installed
gem install bundler -v 2.3.20
rbenv rehash
```

### 4. Install the site's gems (one-time, or after Gemfile changes)

Still from inside this repo's directory:

```bash
bundle config set --local path 'vendor/bundle'   # vendor gems into the repo instead of system-wide
bundle install
```

`vendor/bundle` and `.bundle/` are gitignored, so this stays local to your machine. If `bundle install` fails for an unrelated reason, delete `Gemfile.lock` and try again.

### 5. Serve the site

```bash
bundle exec jekyll serve --config _config.yml,_config.dev.yml
```

Then open 

```bash
http://localhost:4000
```

**Port already in use?** Closing the browser tab does not stop the server — the `jekyll serve` process keeps running in the background and holding port 4000, so a rerun fails with `Address already in use - bind(2) for 127.0.0.1:4000`. Find and kill it, then restart:

```bash
lsof -nP -iTCP -sTCP:LISTEN | grep 4000   # find the PID listening on port 4000
kill <PID>                                 # stop it (use kill -9 <PID> if it won't stop)
```

The dev config (`_config.dev.yml`) disables analytics and points the site at `localhost` instead of the live URL. The server watches for changes and rebuilds automatically; refresh the browser to see them.

For the browser to also auto-refresh on change, add Jekyll's native `--livereload` flag instead: `bundle exec jekyll serve --config _config.yml,_config.dev.yml --livereload`. **Do not use `jekyll liveserve`** (the `hawkins` gem) — it's incompatible with the vendored Jekyll 3.9.2 and returns a 500 error on every request (`undefined method 'key?' for nil:NilClass` in WEBrick's charset handling, since `hawkins` never sets `:MimeTypesCharset`). If you're hitting a blank page or that error, check for a stray `jekyll liveserve` process (`lsof -nP -iTCP -sTCP:LISTEN | grep 4000`), kill it, and restart with `--livereload` as above.

Steps 1-4 only need to be redone if you switch machines or the `Gemfile` changes; day to day, step 5 is all you need.

**Troubleshooting: `bundler: command not found: jekyll`.** This means your shell isn't actually using the rbenv-managed Ruby, even if your terminal prompt shows the right version (some prompt themes just read `.ruby-version` as text, without checking whether rbenv is really active). Confirm with `type ruby` — it should print a path under `~/.rbenv/shims`, not `/usr/bin/ruby`. If it prints the wrong path, step 2 (`eval "$(rbenv init - zsh)"` in `~/.zshrc`) either wasn't added or hasn't taken effect yet in this shell — open a new terminal window/tab (or run `source ~/.zshrc`) and try again.

## Adding content

### A blog post

Add a file to `_posts/`, named `YYYY-MM-DD-title.md`, with front matter like:

```yaml
---
title: "My post title"
date: 2026-01-01
---
```

It shows up automatically under the "Posts" nav link (`/year-archive/`).

### A publication, talk, or software package entry

These are collections, each with its own directory and archive page:

* `_publications/` → `/publications/` (see `markdown_generator/pubsFromBib.py`/`publications.py` for bulk-generating entries from BibTeX/TSV, or fetch from your InspireHEP profile)
* `_talks/` → `/talks/`
* `_software/` → `/software/`

Add a new Markdown file to the relevant directory with front matter matching the existing entries in that collection (e.g. `title`, `date`, `venue`, `permalink`); it shows up automatically on the matching archive page.

### A standalone page

Add a file to `_pages/` with front matter setting at least `title` and `permalink`:

```yaml
---
title: "My New Page"
permalink: /my-new-page/
author_profile: true
---
```

To surface it in the top nav, add an entry to `_data/navigation.yml`.

### CV, About, or Resources content

Edit the relevant file directly in `_pages/`: `cv.md`, `about.md`, `gw.md`, `ai-and-ml.md`, `cheat-sheets.md`.

## Repo layout

- `_pages/` — standalone pages (About, CV, Projects, Resources, ...)
- `_posts/` — blog posts
- `_data/navigation.yml` — top nav bar links
- `_data/authors.yml` — sidebar author info
- `_layouts/`, `_includes/`, `_sass/` — theme templates and styles (avoid changing these unless customizing the theme itself)
- `files/` — uploaded PDFs etc., served at `/files/<name>`
- `markdown_generator/` — optional scripts/notebooks to bulk-generate talk/publication Markdown files from a TSV

See `CLAUDE.md` for more detail on the architecture.

## Notes

- If GitHub flags a security vulnerability in `Gemfile.lock`, delete it and run `bundle install` again.
- This started as a fork of [academicpages](https://github.com/academicpages/academicpages.github.io) (MIT licensed, see `LICENSE`), itself a fork of [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/).

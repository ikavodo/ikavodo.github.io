# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal Jekyll blog (ikavodo.github.io) using the [Indigo theme](https://github.com/sergiokopplin/indigo), deployed via GitHub Pages. Posts cover math, algorithms, music, and computer vision — many with LaTeX via MathJax and embedded Python-generated plots.

## Local development

**With Docker (preferred):**
```bash
docker compose up
# Site served at http://localhost:4000 with live reload
```

**Without Docker:**
```bash
bundle install
bundle exec jekyll serve
# Site served at http://localhost:4000
```

Jekyll is configured with `future: true`, so posts dated in the future are rendered locally but also on the live site.

## Adding a post

Create a file in `_posts/` named `YYYY-MM-DD-slug.md` (or `.markdown`). Required front matter:

```yaml
---
title: "Post Title"
layout: post
date: 2026-01-01 12:00
tags:
  - Tag1
category: blog        # or: project
author: Ido Akov
description: "Short description for SEO/social."
---
```

Optional front matter fields:
- `image: /assets/images/foo.png` + `headerImage: true` — displays image as post header
- `star: true` — marks the post as featured
- `hidden: true` — hides the post from listing pages but keeps it accessible by URL

## Math and code

- **LaTeX**: use `$$...$$` for display math, `\\(...\\)` for inline. Rendered by MathJax (configured in `_config.yml` via kramdown's `math_engine: mathjax`).
- **Code blocks**: fenced with triple backticks; syntax highlighted by Rouge.
- **Plots/images**: store under `assets/images/` and reference with absolute paths like `/assets/images/foo.png`.

## Site architecture

| Path | Role |
|------|------|
| `_config.yml` | All site-wide settings: author, social links, plugins, kramdown/MathJax config |
| `_layouts/` | `default.html` → base shell; `page.html` → generic page; `post.html` → blog post (header image, tags, prev/next, related, author block, Disqus) |
| `_includes/` | Partials injected by layouts: `header.html`, `footer.html`, `nav.html`, `author.html`, `related.html`, `disqus.html`, `style.scss`, `style-dark.scss` |
| `_sass/` | SCSS split into `base/` (variables, normalize, syntax, general), `components/` (nav, footer, author, spoiler, side-by-side…), `pages/` (post, page, tags, home-blog-projects) |
| `_posts/` | All content — Markdown files with YAML front matter |
| `assets/` | Static files: images, CV PDF, JS |
| `blog.html`, `projects.html`, `tags.html` | Listing pages for each content type |

The Disqus comment system is enabled per-post based on `category` matching `site.disqus.categories` (`[blog, project]`). The `post-advance-links` config controls which categories get prev/next navigation (currently `[blog]`).

Dark mode is handled by a parallel `style-dark.scss` / `variables-dark.sass` / `syntax-dark.sass` stack under `_includes/` and `_sass/base/`.

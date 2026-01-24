# smallwat3r.com

Personal website and blog.

## Build dependencies

- Python 3
- [Pandoc](https://pandoc.org/) for content conversion

## Build

```
make
```

Outputs `dist/` and `dist.zip`.

## Writing posts

Posts are written in [Djot](https://djot.net/), a markup language by John
MacFarlane (creator of Pandoc). It fixes Markdown's parsing ambiguities,
making conversion more predictable. Since we use Pandoc to convert to HTML,
djot is a natural fit.

Create a djot file in `content/blog/` with YAML frontmatter:

```djot
---
title: Post title
description: Brief description for meta tags.
date: 2026-01-24T10:30
lastmod: 2026-01-24T12:00  # optional, defaults to date
---

Your content here.
```

## License

Content is copyrighted. Code is MIT.

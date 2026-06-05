#!/usr/bin/env python3
"""Build script for smallwat3r.com"""

import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from math import ceil
from operator import attrgetter
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

DOMAIN = "https://smallwat3r.com"
CONTENT = Path("content")
BUILD = Path(".build")
STATIC = Path("static")
TEMPLATES = Path("templates")
DIST = Path("dist")


@dataclass
class Content:
    slug: str
    path: str
    title: str
    description: str
    date: str
    lastmod: str
    body: str
    read_time: int = 0
    tags: tuple[str, ...] = ()


def calc_read_time(html: str) -> int:
    """Calculate read time in minutes from HTML content (~200 wpm)."""
    text = re.sub(r"<[^>]+>", "", html)
    return ceil(len(text.split()) / 200)


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse YAML frontmatter from file."""
    _, frontmatter, _ = path.read_text().split("---", 2)
    meta = {}
    for line in frontmatter.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta


def collect_content(path: Path, prefix: str = "") -> Content:
    """Collect metadata and body from a content file."""
    meta = parse_frontmatter(path)
    for field in ("title", "description", "date"):
        if field not in meta:
            raise SystemExit(f"Error: {path} missing required field: {field}")
    slug = path.stem
    body = (BUILD / prefix / f"{slug}.html").read_text()
    tags = tuple(t.strip() for t in meta.get("tags", "").split(",") if t.strip())
    return Content(
        slug=slug,
        path=f"{prefix}{slug}.html",
        title=meta["title"],
        description=meta["description"],
        date=meta["date"],
        lastmod=meta.get("lastmod", meta["date"]),
        body=body,
        read_time=calc_read_time(body),
        tags=tags,
    )


def create_jinja_env() -> Environment:
    """Create Jinja2 environment with filters and globals."""
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    env.globals["domain"] = DOMAIN
    env.globals["year"] = datetime.now().year
    env.filters["date_display"] = lambda d: datetime.fromisoformat(d).strftime("%d %b %Y")
    env.filters["date_short"] = lambda d: d.split("T")[0]
    env.filters["rfc822"] = lambda d: format_datetime(
        datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
    )
    return env


def write(path: str, content: str) -> None:
    """Write content to dist."""
    (DIST / path).write_text(content)
    print(f"  {path}")


def build() -> None:
    """Build the site."""
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(parents=True)
    shutil.copytree(STATIC, DIST, dirs_exist_ok=True)
    (DIST / "blog").mkdir(exist_ok=True)

    env = create_jinja_env()

    posts = sorted(
        [collect_content(p, "blog/") for p in (CONTENT / "blog").glob("*.dj")],
        key=attrgetter("date"),
        reverse=True,
    )
    all_tags = sorted({t for p in posts for t in p.tags})
    about = collect_content(CONTENT / "about.dj")
    index = collect_content(CONTENT / "index.dj")

    print("Building:")
    for post in posts:
        write(
            f"blog/{post.slug}.html",
            env.get_template("blog.html").render(post=post),
        )
    write(
        "about.html",
        env.get_template("about.html").render(page=about),
    )
    write(
        "index.html",
        env.get_template("index.html").render(
            index=index, posts=posts, tags=all_tags,
        ),
    )
    write(
        "sitemap.xml",
        env.get_template("sitemap.xml").render(
            posts=posts, about=about, index=index,
        ),
    )
    write("feed.xml", env.get_template("feed.xml").render(posts=posts, index=index))

    shutil.make_archive("dist", "zip", DIST)
    print("Done")


if __name__ == "__main__":
    build()

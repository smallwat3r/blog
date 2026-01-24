#!/usr/bin/env python3
"""Build script for smallwat3r.com"""

import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
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


def parse_frontmatter(md_path: Path) -> dict:
    """Parse frontmatter from markdown file."""
    _, frontmatter, _ = md_path.read_text().split("---", 2)
    return {k.strip(): v.strip() for line in frontmatter.strip().split("\n")
            if ":" in line for k, v in [line.split(":", 1)]}


def collect_content(md_path: Path, path_prefix: str = "") -> Content:
    """Collect metadata from a markdown file."""
    meta = parse_frontmatter(md_path)
    for field in ("title", "description", "date"):
        if field not in meta:
            raise SystemExit(f"Error: {md_path} missing required frontmatter: {field}")
    slug = md_path.stem
    return Content(
        slug=slug,
        path=f"{path_prefix}{slug}.html",
        title=meta["title"],
        description=meta["description"],
        date=meta["date"],
        lastmod=meta.get("lastmod", meta["date"]),
        body=(BUILD / path_prefix / f"{slug}.html").read_text(),
    )


def create_jinja_env() -> Environment:
    """Create Jinja2 environment with custom filters and globals."""
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    env.globals["domain"] = DOMAIN
    env.globals["year"] = datetime.now().year
    env.filters["date_display"] = lambda d: datetime.fromisoformat(d).strftime("%B %Y")
    env.filters["date_short"] = lambda d: d.split("T")[0]
    env.filters["rfc822"] = lambda d: format_datetime(
        datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
    )
    return env


def write(path: str, content: str) -> None:
    """Write content to dist and print status."""
    (DIST / path).write_text(content)
    print(f"Generated dist/{path}")


def build() -> None:
    """Build the site."""
    print("Building...")

    # Clean and create dist
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(parents=True)

    # Copy static files
    shutil.copytree(STATIC, DIST, dirs_exist_ok=True)
    (DIST / "blog").mkdir(exist_ok=True)

    env = create_jinja_env()

    # Collect contents
    posts = sorted(
        [collect_content(p, "blog/") for p in (CONTENT / "blog").glob("*.dj")],
        key=attrgetter("date"), reverse=True
    )
    about = collect_content(CONTENT / "about.dj")
    index = collect_content(CONTENT / "index.dj")

    # Generate files
    template = env.get_template("blog.html")
    for post in posts:
        write(f"blog/{post.slug}.html", template.render(post=post))
    write("about.html", env.get_template("about.html").render(page=about))
    write("index.html", env.get_template("index.html").render(index=index, posts=posts))
    write("sitemap.xml", env.get_template("sitemap.xml").render(posts=posts, about=about, index=index))
    write("feed.xml", env.get_template("feed.xml").render(posts=posts, index=index))

    # Create zip
    shutil.make_archive("dist", "zip", DIST)
    print("Done: dist/")


if __name__ == "__main__":
    build()

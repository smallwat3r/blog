#!/usr/bin/env python3
"""Build script for smallwat3r.com"""

import json
import re
import shutil
import urllib.request
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


@dataclass
class Repo:
    name: str
    description: str
    url: str
    stars: int
    forks: int
    language: str
    pushed_at: str


def fetch_github_repos(user: str) -> list[Repo]:
    """Fetch public repos from GitHub, sorted by stars."""
    repos: list[Repo] = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{user}/repos?per_page=100&page={page}"
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        if not data:
            break
        for r in data:
            if r["fork"] or r["archived"]:
                continue
            pushed = r["pushed_at"] or ""
            if pushed:
                pushed = pushed.split("T")[0]
            repos.append(Repo(
                name=r["name"],
                description=r["description"] or "",
                url=r["html_url"],
                stars=r["stargazers_count"],
                forks=r["forks_count"],
                language=r["language"] or "",
                pushed_at=pushed,
            ))
        page += 1
    repos.sort(key=lambda r: r.stars, reverse=True)
    return repos


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
    projects = collect_content(CONTENT / "projects.dj")
    index = collect_content(CONTENT / "index.dj")

    print("Fetching GitHub repos...")
    repos = fetch_github_repos("smallwat3r")
    fetched_at = datetime.now(timezone.utc).strftime("%d %b %Y at %H:%M UTC")

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
        "projects.html",
        env.get_template("projects.html").render(
            page=projects, repos=repos, fetched_at=fetched_at,
        ),
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
            posts=posts, about=about,
            projects=projects, index=index,
        ),
    )
    write("feed.xml", env.get_template("feed.xml").render(posts=posts, index=index))

    shutil.make_archive("dist", "zip", DIST)
    print("Done")


if __name__ == "__main__":
    build()

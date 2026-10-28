#!/usr/bin/env python3
"""Render a small SVG using public GitHub profile and repository data."""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


USERNAME = os.environ.get("GITHUB_USERNAME", "fertfert")
API_ROOT = "https://api.github.com"
OUTPUT = Path(__file__).resolve().parents[2] / "assets" / "github-stats.svg"


def get_json(path: str) -> object:
    request = urllib.request.Request(
        f"{API_ROOT}/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-profile-stats",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def render_card(public_repos: int, stars: int, followers: int) -> str:
    metrics = (
        ("PUBLIC REPOSITORIES", public_repos),
        ("STARS EARNED", stars),
        ("FOLLOWERS", followers),
    )
    columns = []
    for index, (label, value) in enumerate(metrics):
        x = 48 + index * 368
        columns.append(
            f'''<g transform="translate({x} 0)">
  <text x="0" y="69" class="label">{html.escape(label)}</text>
  <text x="0" y="126" class="value">{value:,}</text>
</g>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="174" viewBox="0 0 1160 174" role="img" aria-labelledby="title desc">
  <title id="title">Timur's GitHub stats</title>
  <desc id="desc">Live counts of public repositories, repository stars, and followers.</desc>
  <defs>
    <linearGradient id="edge" x1="0" x2="1">
      <stop offset="0" stop-color="#E53935" />
      <stop offset="1" stop-color="#681B28" />
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="1158" height="172" rx="18" fill="#0D1117" stroke="#30363D" />
  <rect x="1" y="1" width="5" height="172" rx="2.5" fill="url(#edge)" />
  <path d="M397 34v106M765 34v106" stroke="#30363D" />
  <style>
    .label {{ fill: #8B949E; font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; letter-spacing: 1.2px; }}
    .value {{ fill: #F0F3F6; font: 700 38px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
  </style>
  {''.join(columns)}
</svg>
'''


def main() -> int:
    try:
        profile = get_json(f"users/{USERNAME}")
        repos = get_json(f"users/{USERNAME}/repos?type=owner&per_page=100&page=1")
        if not isinstance(profile, dict) or not isinstance(repos, list):
            raise ValueError("GitHub returned an unexpected response")

        stars = sum(
            int(repo.get("stargazers_count", 0))
            for repo in repos
            if isinstance(repo, dict) and not repo.get("fork", False)
        )
        svg = render_card(
            int(profile.get("public_repos", 0)),
            stars,
            int(profile.get("followers", 0)),
        )
        OUTPUT.write_text(svg, encoding="utf-8")
        print(f"Updated public profile stats for {USERNAME}.")
        return 0
    except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"Could not refresh public GitHub stats; keeping the local fallback: {exc}")
        return 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import json
import urllib.request
import urllib.error
from packaging.version import Version, InvalidVersion

GITHUB_OWNER = "MaximilianOesterwinter"
GITHUB_REPO = "R-Tool"

def normalize_version(tag: str) -> str:
    
    return tag.strip().removeprefix("v").removeprefix("V")

def get_latest_release() -> dict | None:
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "R-Tool"
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None

def is_newer_version_available(current_version: str) -> tuple[bool, dict | None]:
    release = get_latest_release()
    if not release:
        return False, None

    tag_name = release.get("tag_name", "").strip()
    if not tag_name:
        return False, None

    try:
        current = Version(normalize_version(current_version))
        latest = Version(normalize_version(tag_name))
    except InvalidVersion:
        return False, release

    return latest > current, release
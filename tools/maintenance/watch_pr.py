import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


GH_EXE = r"C:\Program Files\GitHub CLI\gh.exe"
OWNER = "dirkste"
REPO = "compass-automation"
PR_NUMBER = 1
POLL_SECONDS = 30


@dataclass(frozen=True)
class SeenKey:
    kind: str  # "issue_comment" | "review" | "review_comment"
    id: int


def _gh_api(path: str) -> object:
    if not path.startswith(f"/repos/{OWNER}/{REPO}/"):
        raise ValueError(f"Unexpected gh api path: {path!r}")
    if not re.fullmatch(r"/[A-Za-z0-9._\-/]+", path or ""):
        raise ValueError(f"Invalid characters in gh api path: {path!r}")

    env = os.environ.copy()
    # If these are set (and invalid), gh will prefer them over the stored auth.
    env.pop("GITHUB_TOKEN", None)
    env.pop("GH_TOKEN", None)
    cmd = [GH_EXE, "api", "-H", "Accept: application/vnd.github+json", path]
    out_bytes = subprocess.check_output(cmd, env=env)
    out_text = out_bytes.decode("utf-8", errors="replace")
    return json.loads(out_text)


def _safe_login(item: dict) -> str:
    user = item.get("user") or item.get("author") or {}
    return user.get("login") or "unknown"


def fetch_events() -> Tuple[List[dict], List[dict], List[dict]]:
    issue_comments = _gh_api(f"/repos/{OWNER}/{REPO}/issues/{PR_NUMBER}/comments")
    reviews = _gh_api(f"/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/reviews")
    review_comments = _gh_api(f"/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/comments")
    return issue_comments, reviews, review_comments


def print_event(kind: str, item: dict) -> None:
    if kind == "issue_comment":
        who = _safe_login(item)
        created = item.get("created_at")
        url = item.get("html_url")
        body = (item.get("body") or "").strip()
        body_preview = body.replace("\r\n", "\n").split("\n")[0][:200]
        print(f"[NEW COMMENT] {who} @ {created} :: {body_preview}\n  {url}")
        return

    if kind == "review":
        who = _safe_login(item)
        state = item.get("state")
        submitted = item.get("submitted_at")
        body = (item.get("body") or "").strip()
        body_preview = body.replace("\r\n", "\n").split("\n")[0][:200]
        url = item.get("html_url") or f"https://github.com/{OWNER}/{REPO}/pull/{PR_NUMBER}"
        print(f"[NEW REVIEW] {who} [{state}] @ {submitted} :: {body_preview}\n  {url}")
        return

    if kind == "review_comment":
        who = _safe_login(item)
        created = item.get("created_at")
        path = item.get("path")
        line = item.get("line") or item.get("original_line")
        url = item.get("html_url")
        body = (item.get("body") or "").strip()
        body_preview = body.replace("\r\n", "\n").split("\n")[0][:200]
        loc = f"{path}:{line}" if path else "(file comment)"
        print(f"[NEW REVIEW COMMENT] {who} @ {created} {loc} :: {body_preview}\n  {url}")
        return


def main() -> None:
    print(f"Watching PR #{PR_NUMBER}: https://github.com/{OWNER}/{REPO}/pull/{PR_NUMBER}")
    print(f"Polling every {POLL_SECONDS}s. Ctrl+C to stop.")

    seen: Set[SeenKey] = set()

    # Seed seen set with current events so we only print new ones.
    try:
        issue_comments, reviews, review_comments = fetch_events()
        for c in issue_comments:
            seen.add(SeenKey("issue_comment", int(c["id"])))
        for r in reviews:
            seen.add(SeenKey("review", int(r["id"])))
        for rc in review_comments:
            seen.add(SeenKey("review_comment", int(rc["id"])))
        print(f"Seeded: {len(issue_comments)} issue comments, {len(reviews)} reviews, {len(review_comments)} review comments")
    except Exception as e:
        print(f"Initial fetch failed: {e}")

    while True:
        try:
            issue_comments, reviews, review_comments = fetch_events()

            for c in issue_comments:
                key = SeenKey("issue_comment", int(c["id"]))
                if key not in seen:
                    seen.add(key)
                    print_event("issue_comment", c)

            for r in reviews:
                key = SeenKey("review", int(r["id"]))
                if key not in seen:
                    seen.add(key)
                    print_event("review", r)

            for rc in review_comments:
                key = SeenKey("review_comment", int(rc["id"]))
                if key not in seen:
                    seen.add(key)
                    print_event("review_comment", rc)

        except subprocess.CalledProcessError as e:
            print(f"gh api failed (will retry): {e}")
        except Exception as e:
            print(f"Watcher error (will retry): {e}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()

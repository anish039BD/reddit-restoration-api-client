#!/usr/bin/env python3

import html
import json
import os
import sys

import praw


SUBREDDIT = os.getenv("REDDIT_SUBREDDIT", "restoration")
LIMIT = int(os.getenv("REDDIT_FETCH_LIMIT", "25"))
ARCHIVE = os.getenv("ARCHIVE_FILE", os.path.expanduser("~/processed_videos.txt"))


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Missing environment variable: {name}", file=sys.stderr)
        sys.exit(2)
    return value


reddit = praw.Reddit(
    client_id=required_env("REDDIT_CLIENT_ID"),
    client_secret=required_env("REDDIT_CLIENT_SECRET"),
    user_agent=required_env("REDDIT_USER_AGENT"),
)
reddit.read_only = True

os.makedirs(os.path.dirname(ARCHIVE) or ".", exist_ok=True)
open(ARCHIVE, "a", encoding="utf-8").close()

with open(ARCHIVE, "r", encoding="utf-8") as f:
    processed = {line.strip() for line in f if line.strip()}


def reddit_video_from_post(post):
    candidates = []

    for media in (getattr(post, "secure_media", None), getattr(post, "media", None)):
        if isinstance(media, dict):
            candidates.append(media)

    for crosspost in (getattr(post, "crosspost_parent_list", None) or []):
        if isinstance(crosspost, dict):
            for key in ("secure_media", "media"):
                media = crosspost.get(key)
                if isinstance(media, dict):
                    candidates.append(media)

    for media in candidates:
        video = media.get("reddit_video")
        if isinstance(video, dict):
            return video

    return None


try:
    result = None

    for post in reddit.subreddit(SUBREDDIT).new(limit=LIMIT):
        if post.id in processed:
            continue

        video = reddit_video_from_post(post)
        if not video:
            continue

        status = video.get("transcoding_status")
        if status not in (None, "completed"):
            continue

        dash_url = html.unescape(video.get("dash_url") or "")
        hls_url = html.unescape(video.get("hls_url") or "")
        media_url = dash_url or hls_url

        if not media_url:
            continue

        result = {
            "id": post.id,
            "title": post.title,
            "permalink": "https://www.reddit.com" + post.permalink,
            "url": media_url,
            "duration": video.get("duration"),
            "width": video.get("width"),
            "height": video.get("height"),
        }
        break

    if result:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({"error": "no_fresh_video"}))

except Exception as exc:
    print(f"REDDIT_FETCH_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
    raise

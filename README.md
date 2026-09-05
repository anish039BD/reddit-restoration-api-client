# Reddit Restoration API Client

A small, read-only Reddit API client for a personal restoration-video automation workflow.

## Purpose

This project is designed to run on a local Ubuntu machine as part of an n8n + Python workflow. It uses Reddit OAuth through PRAW to read public posts from `r/restoration`, identify native Reddit-hosted videos, skip posts that were already processed, and return direct Reddit media manifest URLs such as DASH or HLS.

The client is read-only. It does **not** post, vote, comment, send messages, access private Reddit data, or modify Reddit content.

## Why this runs outside Devvit

The wider workflow depends on external local tools and services, including:

- n8n for orchestration
- Python for API access and processing
- yt-dlp for media retrieval
- FFmpeg for local video processing
- local speech synthesis and transcription tools

Because these components run on the user's Ubuntu machine and require local file-system/process access, the workflow cannot run entirely inside the Devvit environment.

## Reddit data accessed

The client only requests public post information needed for the workflow, including:

- post ID
- title
- permalink
- native Reddit video metadata
- DASH/HLS media manifest URLs when available

## Authentication

OAuth credentials are supplied through environment variables and are never stored in source code:

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT='linux:restoration-shorts:v1.0 (by u/YOUR_REDDIT_USERNAME)'
```

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
python3 fetch_reddit.py
```

Example successful output:

```json
{
  "id": "example_id",
  "title": "Example restoration post",
  "permalink": "https://www.reddit.com/r/restoration/comments/...",
  "url": "https://v.redd.it/.../DASHPlaylist.mpd"
}
```

If no fresh native Reddit video is found:

```json
{"error": "no_fresh_video"}
```

## Rate limits and responsible use

The client uses authenticated Reddit API access through PRAW and is intended for low-volume, personal, read-only use. It does not attempt to bypass Reddit access controls, Cloudflare, or API rate limits.

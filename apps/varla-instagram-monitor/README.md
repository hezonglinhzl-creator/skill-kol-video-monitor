# Varla Instagram Monitor

This monitor keeps only the latest public metrics for Varla-related Instagram Reel content.

Milestone logic is intentionally not present:

- No `D7_views`, `D15_views`, `D30_views`
- No `D7_likes`, `D15_likes`, `D30_likes`
- No `D7_comments`, `D15_comments`, `D30_comments`
- No `milestones.py`
- No schedule based on post age

## Commands

```powershell
python main.py discover
python main.py update
python main.py sync
python main.py all
```

`python main.py all` runs:

1. discover
2. update current Views, Followers, Likes, Comments
3. aggregate KOL ranking
4. sync

## Data Rules

Instagram Reel `shortcode` is the unique content ID.

Views are collected from the author's `/reels/` grid only by exact matching the anchor href shortcode:

- database shortcode
- author's Reels Grid anchor href shortcode

Do not match by cover image, AI vision, video position, publish time, or caption.

When a view count cannot be read, do not write `0`. Keep the previous successful Views value and update `view_status`, such as `PARSE_FAILED`, `NOT_FOUND`, or `RATE_LIMITED`.

`first_seen_at` is written only on first discovery. `last_checked_at` is updated after each successful metric collection.

## Inputs

Until the browser collector is wired into this folder, place collected records in:

- `data/discovery_input.json`
- `data/update_input.json`

Each file can be either a JSON list or an object with a `records` list.

Example record:

```json
{
  "username": "creator_name",
  "profile_url": "https://www.instagram.com/creator_name/",
  "post_url": "https://www.instagram.com/reel/SHORTCODE/",
  "shortcode": "SHORTCODE",
  "followers": 12000,
  "views": 3456,
  "likes": 120,
  "comments": 8,
  "classification": "Varla M7S",
  "discovery_source": "varla_adventure",
  "view_status": "OK"
}
```

## Feishu Fields

Content Monitor:

`Username`, `Profile URL`, `Post URL`, `Shortcode`, `Followers`, `Views`, `Likes`, `Comments`, `Classification`, `Discovery Source`, `First Seen`, `Last Checked`, `View Status`

KOL Ranking:

`Username`, `Profile URL`, `Followers`, `Varla Content Count`, `Total Views`, `Average Views`, `Max Views`, `Total Likes`, `Total Comments`, `Engagement Rate`, `Views / Followers`, `Last Checked`

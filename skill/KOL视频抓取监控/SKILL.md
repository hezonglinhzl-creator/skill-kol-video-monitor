---
name: KOL视频抓取监控
description: Use whenever discovering, crawling, refreshing, cleaning, grouping, deduplicating, comparing, or syncing Varla social video data from public Instagram, TikTok, YouTube, Meta Business Suite, Meta CSV exports, SQLite, or Feishu Base. This is the single entry point for KOL public metrics, exact Instagram shortcode matching, current Views/Likes/Comments/Followers, first_seen_at/last_checked_at, View Status, KOL Ranking, Varla-owned Business Suite reach/interactions/shares/saves, 播放量, 点赞, 评论, 粉丝量, 关注数量, 重复名字, 重复链接, creator grouping, and daily local runs.
---

# KOL视频抓取监控

Use this skill for the Varla KOL video tracking table in Feishu Base. The user usually wants real table edits, not a plan. Work against the actual Feishu Base and verify by reading the table back.

## Fixed IDs

Unless the user provides a different table, the target table is:

- Base token: `VZ58b0AKdaJNiAs3kc7cOOGZncc`
- Video table: `tblAZ234s8zfn3iy`
- Video view: `vewaG9iRnx`
- Source KOL table: `tblKwzo7QwvYhtjy`
- Source KOL view: `vewqH4Lvrl`

## Environment

- Run PowerShell through PowerShell 7.1:
  `C:\Users\<your-user>\Tools\PowerShell-7.1.7\pwsh.exe`
- For scripts that print localized captions or titles, set `PYTHONIOENCODING=utf-8` in the PowerShell process so a Windows GBK console error does not interrupt a crawl after artifacts have already been saved.
- Use `lark-cli base` for Feishu Base operations.
- Use `--json "@path\to\payload.json"` for large batch updates. Do not pass huge JSON directly on the command line because Windows can fail with filename/argument length errors.
- Before browser automation, warn the user that social sites can detect automation and there is account risk.

## Instagram Current-Data Monitor

Use the local project at `C:\Users\<your-user>\Documents\电摩项目\varla_instagram_monitor` when the request concerns repeatable Instagram discovery, current public metric refreshes, SQLite history, Content Monitor, KOL Ranking, or a daily local run.

This project intentionally maintains only the latest publicly visible metrics. Do not add or restore milestone snapshots:

- no `D7_views`, `D15_views`, or `D30_views`
- no `D7_likes`, `D15_likes`, or `D30_likes`
- no `D7_comments`, `D15_comments`, or `D30_comments`
- no `milestones.py`
- no scheduling or branching based on content age or publication-date milestones

Use these commands from the project directory:

```powershell
python main.py discover
python main.py update
python main.py sync
python main.py all
```

`python main.py all` must run this order:

1. discover new Varla-related Instagram content
2. fill or refresh Views by exact shortcode match
3. refresh current Followers, Likes, and Comments
4. recalculate KOL aggregate data
5. sync Content Monitor and KOL Ranking to Feishu

The current project accepts browser-collector output through `data/discovery_input.json` and `data/update_input.json`. Each input may be a JSON array or an object containing a `records` array. Never claim that `main.py all` performed a live crawl when those files were not refreshed by a browser collector during the same run; report whether the run was live-collected or input-driven.

### SQLite identity and timestamps

- Treat Reel `shortcode` as the unique content ID and SQLite primary key.
- Set `first_seen_at` only when the shortcode is first inserted. Never modify it on later runs.
- Update `last_checked_at` after a successful metric collection for that content.
- Current Followers, Likes, Comments, and Views may replace their older values when a fresh public value is successfully read.
- When Views cannot be read, never write `0` and never erase the previous successful Views value. Preserve it and set `view_status` to a meaningful result such as `PARSE_FAILED`, `NOT_FOUND`, `RATE_LIMITED`, `SCROLL_LIMIT`, or `NO_PUBLIC_VIDEO_VIEWS`.
- Do not silently mark `last_checked_at` as a successful live check when no public page was successfully collected. Preserve the prior value and report the failed status.

### Instagram collection contract

For every discovered or refreshed item:

1. Extract the database shortcode from the exact post URL.
2. Verify the author on the stable `https://www.instagram.com/p/SHORTCODE/` page.
3. Read current Followers, Likes, and Comments from public author/post surfaces when exposed.
4. Open the verified author's `/reels/` page.
5. Locate the Reel card whose anchor href contains the exact same shortcode.
6. Read Views from that exact card, preferring the number adjacent to the views icon in card HTML when visible text is ambiguous.
7. Save source URL, collection time, raw value, normalized integer, and status in the run artifacts before updating SQLite.
8. Recalculate the KOL aggregate only after content upserts finish.
9. Sync Feishu and read the written records back.

Never identify a Reel by cover image, AI vision, grid position, publish date, caption similarity, or the currently playing item in Instagram's infinite Reels feed.

### Feishu monitor schemas

Content Monitor contains only:

`Username`, `Profile URL`, `Post URL`, `Shortcode`, `Followers`, `Views`, `Likes`, `Comments`, `Classification`, `Discovery Source`, `First Seen`, `Last Checked`, `View Status`

KOL Ranking contains only:

`Username`, `Profile URL`, `Followers`, `Varla Content Count`, `Total Views`, `Average Views`, `Max Views`, `Total Likes`, `Total Comments`, `Engagement Rate`, `Views / Followers`, `Last Checked`

Do not add milestone columns to either table. Upsert Content Monitor by `Shortcode` and KOL Ranking by canonical `Username`; do not create duplicate rows on repeat runs.

### Daily local run

For a scheduled local run, use PowerShell 7.1, run `python main.py all` from the monitor project, save a dated run report under `outputs/`, and include:

- discovery, update, aggregate, and sync counts
- live-collected versus input-driven mode
- per-status counts for `View Status`
- rows whose public metrics were unavailable
- Feishu create/update counts and readback results

An unchanged metric is a valid current result. Do not notify on every unchanged daily run unless the user asks; report failures, required login/action, material new content, or completed updates.

## Table Rules

Use only the existing fields in the video table. Do not create or write any “自动采集” fields.

Existing business fields:

- `发布日期`
- `频道名`
- `平台`
- `粉丝量`
- `发布车型`
- `播放量`
- `点赞量`
- `评论数量/相关程度`
- `关注数量`
- `引流`
- `投入`
- `转化`
- `roi`
- `联盟名`
- `视频链接`
- `视频描述`
- `合作/视频问题`
- `kol画像`

Keep `视频链接` clickable. For URL-style text fields, write either the original Markdown link or a Markdown link like:

```text
[https://www.instagram.com/p/SHORTCODE/](https://www.instagram.com/p/SHORTCODE/)
```

Meta Business Suite CSV exports are from the Varla asset perspective. Do not treat CSV `浏览量`, `赞`, `评论`, or `分享` as the creator/KOL public metrics unless the user explicitly reverses this rule in a later request. CSV `关注者数` is post-attributed follows to Varla, not the KOL's follower count.

When the user says “按 k 算”, format large display values like the table:

- `10190` -> `10.2k`
- `6468` -> `6.5k`
- `5309` -> `5.3k`
- `12000` -> `12k`
- `2500` -> `2.5k`
- Leave small counts such as comments and `关注数量` as integers.

For current table convention:

- `播放量`: public creator-side views from the linked IG/TK/YTB page; use `k`/`m` display for values over 1000.
- `点赞量`: public creator-side likes from the linked IG/TK/YTB page; use `k`/`m` display for values over 1000.
- `评论数量/相关程度`: public creator-side comments from the linked IG/TK/YTB page; integer.
- `粉丝量`: the KOL/creator account's total follower count; never fill it from CSV `关注者数`.
- `关注数量`: follows attributed to that specific post; map Meta CSV `关注者数` here. A real `0` is valid.
- `引流`: a separate business metric; do not infer it from CSV `关注者数` or public likes/comments/views.

## Meta Business Suite Asset Metrics

Use this section when the user asks for Varla-owned Instagram/Facebook performance shown in an authorized Meta Business Suite session, including reach, interactions, shares, saves, or named collaboration rows. These are Varla asset-side Insights, not the creator's complete public account analytics.

Keep the two metric scopes separate:

- Public KOL scope: collect current creator-side Followers, Views, Likes, and Comments from exact public IG/TK/YTB links using the platform rules below.
- Varla asset scope: collect only the metrics visibly shown by Meta Business Suite for content managed by the Varla account.
- Do not overwrite public KOL `播放量`, `点赞量`, or `评论数量/相关程度` with Business Suite or CSV values unless the user explicitly requests Varla-side metrics in those fields.
- Record the source and snapshot time so later readers can tell which scope produced the value.

### Valid named collaboration rows

When the user asks for `带名字共创`, retain only rows that satisfy all of these:

1. The visible content type is `Reels`.
2. A named third-party account or handle is shown.
3. The row is not published only by `Varla Scooter`, `varla_adventure`, or another owned account.

Exclude cross-post-only quick stories, rows without a named third-party account, and brand-only posts. Do not infer collaboration from a caption alone.

### Business Suite capture procedure

1. Confirm the requested date range, active account, and filters in Business Suite.
2. Capture the visible title/caption, publication date, creator handle, views, reach, interactions, likes, comments, shares, and saves when exposed.
3. For a whole-list request, scroll in bounded steps and deduplicate by exact public post URL when available; otherwise use creator handle plus publication date plus title/caption as an asset-side fallback key.
4. Stop at the grid bottom or after two consecutive scrolls produce no new rows.
5. Keep unavailable values blank or `--`; never convert missing metrics to zero.
6. Treat the visible Business Suite table as the source of truth for that snapshot and do not claim broader creator analytics access.

### Business Suite to Feishu mapping

Use the user-provided Base/table/view and preserve unrelated fields. Only populate `视频链接` when the exact public post URL is genuinely visible; a profile URL belongs in the source note, not the video-link field.

| Meta Business Suite | Feishu field |
| --- | --- |
| creator handle | `频道名` |
| Instagram/Facebook | `平台` |
| model visibly named in title/caption | `发布车型` |
| views | `播放量` only for an explicitly requested Varla asset-side report |
| likes | `点赞量` only for an explicitly requested Varla asset-side report |
| comments | `评论数量/相关程度` only for an explicitly requested Varla asset-side report |
| short title/caption | `视频描述` |
| source, snapshot time, reach, interactions, shares, saves | `合作/视频问题` |

Use this note format:

```text
Meta Business Suite snapshot YYYY-MM-DD HH:mm; scope: Varla asset; profile: https://www.instagram.com/HANDLE/; reach N; interactions N; shares N; saves N. Exact post URL was not exposed in the current performance table.
```

If an exact post URL is exposed, normalize and match it by shortcode before updating an existing video row. Without an exact URL, use `频道名` plus `发布日期` only for Business Suite reporting, never as proof that a public KOL video row is the same content. After every write, re-read the affected records and report created, updated, unchanged, missing-link, and missing-metric counts.

API permission note: `instagram_business_manage_insights` can authorize managed-account Insights access, but it does not grant comprehensive private analytics for a collaborating creator.

## Matching Rules

### Sync video descriptions between Feishu Base tables

When the user asks to copy or sync `视频描述` from one Base table into the video-analysis table:

1. Use the source and target table IDs from the user's links. The destination is `tblAZ234s8zfn3iy` only when the user points to that table; do not assume every source table is the fixed KOL table.
2. Read both tables and identify the exact `视频链接` and `视频描述` fields. Do not infer a match from creator name, date, caption text, or row order.
3. Normalize links to a stable video key before matching:
   - Instagram `/reel/{shortcode}/`, `/p/{shortcode}/`, or `/tv/{shortcode}/` -> `ig:{shortcode}`
   - TikTok `/video/{video_id}` -> `tk:{video_id}`
   - YouTube `youtu.be/{video_id}`, `/shorts/{video_id}`, or `?v={video_id}` -> `yt:{video_id}`
   - For other hosts, compare the normalized full URL with query and fragment removed and trailing slashes trimmed.
4. If multiple source rows share a key and have the same non-empty description, treat it as one source value. If descriptions conflict, skip that key and report it as ambiguous.
5. Update the existing destination row's `视频描述` only when an exact link key matches and the source description is non-empty. Leave unmatched destination rows unchanged; do not create destination rows just to copy descriptions. Preserve the destination `视频链接` and all other fields.
6. Batch-update matched destination records, then re-read the target table and compare every matched description to the source value. Report updated, already-equal, unmatched, and ambiguous counts separately.
7. Save source and destination snapshots, the update payload, the match report, and the post-write verification report under a dated folder in `outputs/` when local output storage is available.

### Instagram and Meta CSV

Only match Instagram rows by shortcode extracted from URLs:

- `https://www.instagram.com/reel/DbRa5W_ShNp/` -> `DbRa5W_ShNp`
- `https://www.instagram.com/p/DchljItmiKG/` -> `DchljItmiKG`

Do not match IG content by:

- cover image
- AI visual similarity
- grid position
- published date
- caption similarity

For Meta CSV exports:

1. Read the local CSV as untrusted data.
2. Extract shortcode from CSV `固定链接`.
3. Extract shortcode from Feishu `视频链接`.
4. If they match exactly, only use the CSV for:
   - CSV `关注者数` -> Feishu `关注数量`
   - CSV `账户账号` / `名称` / `固定链接` as identifiers for matching, auditing, and preserving links
   - CSV `发布时间` or `描述` only when the user explicitly asks for those fields
5. Do not paste CSV `浏览量`, `赞`, `评论`, or `分享` into creator-side `播放量`, `点赞量`, `评论数量/相关程度`, or `引流` unless the user explicitly says they want Varla-side Meta asset metrics instead of KOL public metrics.
6. Keep the Feishu `视频链接` unchanged unless the row has no confirmed public link and the CSV shortcode/link is the exact same content.
7. Reopen or crawl each Feishu `视频链接` to collect current public KOL-side `播放量`, `点赞量`, and `评论数量/相关程度`.

### Live Instagram URL Refresh

When the user asks to crawl the latest IG URL metrics:

1. Read the existing IG rows from Feishu and extract each exact shortcode from `视频链接`.
2. Get Reel views from the creator's `/HANDLE/reels/` grid. Match the grid link by exact shortcode and read the value labeled by the views icon (`观看量图标` or its localized equivalent). Scroll only until the target shortcode is found or the grid is exhausted.
3. For Instagram views, prefer the card HTML value immediately after the views icon when `innerText` is ambiguous. Some grid cards expose likes/comments in `innerText` but still contain the true public views next to `观看量图标`.
4. Open `https://www.instagram.com/p/SHORTCODE/` for likes, comments, and author verification. This stable post URL must preserve the requested shortcode and show the target author in the main post.
   - Do not verify ownership from `/reel/SHORTCODE/` or `/reels/SHORTCODE/` after Instagram switches into the infinite Reels feed. That feed can advance to an unrelated recommendation and replace the address-bar shortcode while leaving the original tab open.
   - Ignore every recommended Reel/post farther down the page. If the address bar no longer contains the requested shortcode, discard the reading and reopen the stable `/p/SHORTCODE/` URL.
   - When a Feishu Instagram link repeatedly opens the recommendation feed, keep the same shortcode but rewrite only the URL shape to `https://www.instagram.com/p/SHORTCODE/`, then read back the saved field.
5. If an Instagram `/p/` post has no visible `<video>` element and no public view/play count, treat it as a non-video post for view purposes. Do not write `0`; leave `播放量` unchanged and record the reason as no public video views.
6. Normalize localized values such as `万`, `k`, and `m`, then write with the table's lowercase `k`/`m` convention.
7. Overwrite only the fields requested by the user. If a value is not exposed, leave that field unchanged and record the reason.
8. For a request limited to views, likes, and comments, do not change `粉丝量`, `关注数量`, or `引流`.

Instagram view parser examples:

- `1.2万` -> `12000`
- `16.2万` -> `162000`
- `3万` -> `30000`
- `9907` -> `9907`
- `1.2K` -> `1200`
- `12K` -> `12000`
- `1.3M` -> `1300000`

Recent verified Instagram views run:

| Date | Scope | Method | Result | Write rule | Evidence |
|---|---:|---|---:|---|---|
| 2026-08-28 | 75 IG rows / 41 creator groups | Current logged-in Chrome, one `/HANDLE/reels/` grid per creator, exact shortcode match, max 20 scrolls | 72 Reel views found and written back | Update only `播放量`; leave failed or non-video posts unchanged; never write `0` | `outputs/instagram_views_only_20260828_181427/verification_report.json` |

Observed Instagram view collection cases from that run:

| Case | Symptom | Fix / decision |
|---|---|---|
| Normal Reel grid card | `innerText` directly exposes values like `16.2万`, `8493`, or `10.2万` | Parse localized count and write lowercase `k`/`m` display to `播放量` |
| Ambiguous Reel grid card | `innerText` exposes likes/comments, but card HTML contains `观看量图标` followed by the true view number | Prefer the number immediately after the views icon in card HTML |
| Instagram `/p/` non-video post | Detail page has no visible `<video>` element and no public view/play count | Treat as no public video views; leave `播放量` unchanged |
| Found but parse failed | Shortcode link is present but no parseable view count is captured | Save debug HTML under `outputs/debug/grid_views/` or run-specific `debug_grid_views/` and do not write a value |
| Scroll limit | Exact shortcode is not found within max scrolls | Mark `SCROLL_LIMIT`; leave `播放量` unchanged |

Do not treat likes as views, infer views from reach, or use metrics from a recommended post. Save the scrape timestamp and exact source URL for each result.

### TikTok and YouTube

Search with the keyword `varla` only. Do not broaden to generic ebike terms unless the user explicitly changes the rule.

For TikTok and YouTube:

1. Start from source KOL rows only when they satisfy the user’s scope, usually:
   - `负责人` contains `何宗霖`
   - `Contact Status` includes `已发货`, `已收货`, `已发布`, or `已完成`
   - there is a contract when the user says unsigned creators do not matter
2. Search public pages for `varla`.
3. Only write rows where the author/handle is confidently the target KOL or an established alias.
4. Open the public video page and capture visible or embedded public data:
   - publish date
   - views
   - likes
   - comments
   - title/caption
   - URL
5. If a field is not publicly shown, leave it blank and note that the public page did not expose it.
6. Never invent data from memory, screenshots, or assumptions.

### Date-window discovery and verification

For monthly catch-up runs, define the user's local date range explicitly. Treat the requested final day as inclusive; convert it to the next day as an exclusive `before:` boundary for YouTube searches. Do not trust relative search labels such as “8 days ago” for row dates. Open each candidate and use the exact publish/upload date from the video page metadata, then check it against the requested range.

Search results are candidate discovery, not proof that a post belongs in the KOL report. For every candidate, confirm the author/handle on the video page and match it to the source KOL table or an established alias in this workflow. Exclude official Varla accounts, scooter-only models outside the user's scope, and accounts whose KOL identity cannot be confirmed. A `varla` hashtag by itself can be insufficient to identify the bike model; leave `发布车型` blank when the video does not establish it, and use a neutral `视频描述` instead of guessing whether it is an unboxing, review, or ride.

Search can miss posts if only the first global results are used. Search the platform with `varla`, then supplement discovery with `varla` plus known eligible KOL handles where needed. Keep all searches within the keyword rule above; do not widen to unrelated generic e-bike searches. Open the exact post URL before writing any metrics. Keep comments blank when the public page does not expose a count; never convert an unavailable count to zero.

### Monthly metric totals

The table stores large view and like counts in rounded `k`/`m` display form. Summing those cells produces an approximate total, not an exact raw-count total (for example, `4.8k` has already lost precision). When reporting totals from the table, label them as based on the table's displayed values. If exact totals are required, sum the captured integer metrics from the run evidence and keep that evidence with the report; do not imply that rounded table values are exact.

Known alias normalization from this workflow:

- `avi__rides`, `avi_rides`, and `Avi_rides` are the same creator group. Keep the group label as `avi__rides` when the IG group exists.
- `example_creator` and `example_creator_` are the same creator group. Keep the group label as `example_creator_` when the IG group exists.

## Grouping and Cleanup

The user wants each creator’s rows together:

1. Group by canonical creator, not only exact displayed text.
2. Put each creator’s IG/TK/YTB rows together.
3. Within a creator group, use a stable platform order:
   - `IG`
   - `TK`
   - `YTB-短`
   - `YTB-长`
4. Keep only the first row’s `频道名` visible.
5. Clear duplicate `频道名` cells on subsequent rows in the same group. Do not delete the data row just because the name is repeated.

Feishu Base may not expose a direct “move record after this row” API. If row movement is needed, reorder the visible row content by batch-updating records in the current view order. Back up/read the current table first.

## Duplicate Links

After every write:

1. Re-read the target table.
2. Normalize video URLs:
   - Instagram by shortcode
   - TikTok by `/video/{id}`
   - YouTube by `v=` or `/shorts/{id}` or `youtu.be/{id}`
3. If duplicate links exist, keep the row with more complete creator grouping and metrics.
4. Clear the duplicate row’s content fields rather than deleting records, unless the user explicitly asks to delete records.

## Verification

Always verify after mutations:

- Re-read the Feishu table.
- Confirm matched row count and updated row count.
- Confirm duplicate link groups are `0`.
- Confirm separated creator groups are `0`.
- Confirm duplicate visible names are `0`.
- Report any rows still missing confirmed public links.
- Save local artifacts in `outputs/`:
  - source table snapshot
  - target table snapshot before update
  - payload JSON
  - match TSV/CSV
  - final verification report

## Communication

Be concise with the user. They care about:

- what was updated
- which source was used
- whether the links stayed intact
- whether duplicate names/links are clean
- which rows could not be verified

Do not over-explain implementation details unless they ask.

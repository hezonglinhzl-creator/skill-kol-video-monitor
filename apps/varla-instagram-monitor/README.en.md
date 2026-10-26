# Instagram Current Metrics Core / Instagram 当前指标监控核心

[简体中文](README.md) | **English**

Maintain current metrics and discovery/check timestamps by shortcode, then aggregate creators.

## Requirements

Python 3.10+; local input processing uses the standard library, while sync needs separate configuration.

## First run

Extract the whole package first. Run the steps below from **this program directory**, not from the ZIP preview. To open PowerShell here on Windows, open the folder in File Explorer, type `powershell` in its address bar and press Enter.

1. Collect real data first and prepare JSON using the record fields in the source.
2. Save discovery records to `data/discovery_input.json` and updates to `data/update_input.json`; create the data directory if needed.
3. Run `python main.py discover` followed by `python main.py update` here.
4. Run `python main.py sync` for a sync payload. Without sync_feishu.py, this exports locally rather than writing Feishu.

### Example input record

```json
{
  "username": "sample_creator",
  "profile_url": "https://www.instagram.com/sample_creator/",
  "post_url": "https://www.instagram.com/reel/SHORTCODE/",
  "shortcode": "SHORTCODE",
  "followers": 12000,
  "views": 3456,
  "likes": 120,
  "comments": 8,
  "view_status": "OK"
}
```

Wrap records in a JSON array. Replace every example value with data actually collected from the corresponding post.

## Expected result

`data/varla_monitor.sqlite3` and `data/feishu_sync_payload.json`.

## Current limits

This core does not log in to or live-crawl Instagram by itself. Unavailable views must not become zero.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Window closes / Python missing | Open PowerShell in this directory, run `python --version`, install Python from python.org with Add Python to PATH if needed, then rerun the documented command. |
| Missing module | Install the program's requirements using the same Python executable used to launch it. |
| Page does not open / port occupied | Check the URL and service log; stop your own conflicting tool before retrying. A browser extension cannot replace its local backend. |
| Workbook cannot be saved | Close the file in Excel/WPS, verify the output path and retry once. |
| Account or Feishu permission failure | Use your own configuration and check resource permissions. Do not copy another person's tokens. |

## Local data

Your credentials, browser sessions, workbooks and outputs are created/configured locally. The public source does not include real customer/creator records, mailboxes, contracts or logged-in accounts.

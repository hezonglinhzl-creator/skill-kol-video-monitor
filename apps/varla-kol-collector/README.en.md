# KOL and Viral Video Collector Kit / KOL 与爆款视频完整采集器

[简体中文](README.md) | **English**

Start the KOL recorder and video center together with the floating Varla browser panel.

## Requirements

Windows, Python 3.10+, Chrome/Edge; network access for initial dependencies.

## First run

Extract the whole package first. Run the steps below from **this program directory**, not from the ZIP preview. To open PowerShell here on Windows, open the folder in File Explorer, type `powershell` in its address bar and press Enter.

1. Run `Install_Environment.bat` to install dependencies.
2. Inside `KOL_recorder`, run `python create_blank_workbook.py` to create your blank tracker.
3. Return here and run `Start_Varla_Collector.bat`.
4. Leave both service windows running: KOL on 8765 and video center on 8766.
5. Load `chrome_extension`, open a target page, review the panel and record the data.

Open in your browser: `http://127.0.0.1:8766`

### Load the browser extension

1. Open Chrome and enter `chrome://extensions/` in its address bar (Edge: `edge://extensions/`).
2. Turn **Developer mode** on, then choose **Load unpacked**.
3. Select `chrome_extension` relative to this program folder. Select the folder containing `manifest.json`, not a ZIP or the parent project.
4. Refresh an already-open supported website and open the extension/panel. The extension only works on the sites listed in its manifest.
5. If backend status is offline, start the local service described above and keep its window open.


## Expected result

KOL output is under `KOL_recorder/outputs`; video results are under `viral_video_finder/outputs`.

## Current limits

No real contacts or result workbooks are preloaded; initialize your own tracker first. Collection alone defaults to not-contacted; contacted status must be explicit.

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

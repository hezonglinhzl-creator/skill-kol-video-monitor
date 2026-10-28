# KOL Recorder Chrome Extension / KOL 记录器 Chrome 插件

[简体中文](README.md) | **English**

Read visible Instagram/TikTok creator fields and write a local Excel tracker.

## Requirements

Windows, Python 3.10+, Chrome/Edge and openpyxl.

## First run

Extract the whole package first. Run the steps below from **this program directory**, not from the ZIP preview. To open PowerShell here on Windows, open the folder in File Explorer, type `powershell` in its address bar and press Enter.

1. Open PowerShell here and run `python -m pip install -r requirements.txt`.
2. Run `python create_blank_workbook.py` to create a blank 16-column tracker only if none exists.
3. Run `start_kol_recorder.bat` and leave its service window open.
4. Load the extension below, open a creator profile, review parsed fields and record the result.

Open in your browser: `http://127.0.0.1:8765`

### Load the browser extension

1. Open Chrome and enter `chrome://extensions/` in its address bar (Edge: `edge://extensions/`).
2. Turn **Developer mode** on, then choose **Load unpacked**.
3. Select `chrome_kol_recorder_extension` relative to this program folder. Select the folder containing `manifest.json`, not a ZIP or the parent project.
4. Refresh an already-open supported website and open the extension/panel. The extension only works on the sites listed in its manifest.
5. If backend status is offline, start the local service described above and keep its window open.


## Expected result

A row appears in `outputs/varla_kol_tracker.xlsx`; close Excel/WPS while writing.

## Current limits

Use only visible page data; hidden emails and unavailable metrics remain blank. Collection alone defaults to not-contacted; contacted status must be explicit.

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

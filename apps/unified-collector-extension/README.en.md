# Varla Unified Collector Extension / Varla 统一采集 Chrome 插件

[简体中文](README.md) | **English**

Switch between KOL records and video collection in one panel.

## Requirements

Chrome/Edge plus the local services on ports 8765 and 8766.

## First run

Extract the whole package first. Run the steps below from **this program directory**, not from the ZIP preview. To open PowerShell here on Windows, open the folder in File Explorer, type `powershell` in its address bar and press Enter.

1. Start the full collector using `apps/varla-kol-collector/README.md` in the same bundle.
2. Alternatively run `start_varla_unified_collector.bat`, which looks for the sibling collector kit.
3. Load the extension below and check both backend statuses in its popup.
4. Open Instagram/TikTok/YouTube, use the Varla panel, review and save.

Open in your browser: `http://127.0.0.1:8766`

### Load the browser extension

1. Open Chrome and enter `chrome://extensions/` in its address bar (Edge: `edge://extensions/`).
2. Turn **Developer mode** on, then choose **Load unpacked**.
3. Select `varla_unified_collector_extension_无Moto版` relative to this program folder. Select the folder containing `manifest.json`, not a ZIP or the parent project.
4. Refresh an already-open supported website and open the extension/panel. The extension only works on the sites listed in its manifest.
5. If backend status is offline, start the local service described above and keep its window open.


## Expected result

Both backend checks succeed and saved records appear in your local output folders.

## Current limits

The browser extension is not a backend. Loading it without the collector cannot write Excel.

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

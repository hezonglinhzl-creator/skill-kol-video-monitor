# KOL Video Collection and Monitoring / KOL 视频采集与数据监控

[简体中文](README.md) | **English**

Collect public creator/video records with browser extensions, maintain current metrics locally, and export or sync configured results.

## Features

- Creator/video extensions and the collector backend
- Exact Instagram shortcode matching and local SQLite records
- Input-driven metric updates, creator aggregates and sync payload exports

## What is included

| Part | Location |
| --- | --- |
| KOL and Viral Video Collector Kit | [varla-kol-collector](../../apps/varla-kol-collector/README.en.md) |
| Instagram Current Metrics Core | [varla-instagram-monitor](../../apps/varla-instagram-monitor/README.en.md) |
| KOL Recorder Chrome Extension | [kol-recorder-extension](../../apps/kol-recorder-extension/README.en.md) |
| Varla Unified Collector Extension | [unified-collector-extension](../../apps/unified-collector-extension/README.en.md) |
| Skill instructions | [SKILL.md](./SKILL.md) |

## 1. Set up the program first

Recommended: run only the complete varla-kol-collector kit. The standalone KOL recorder is an alternative, not a second service to start on the same 8765 port. Load one collector extension variant at a time.

### KOL and Viral Video Collector Kit (`varla-kol-collector`)

Windows, Python 3.10+, Chrome/Edge; network access for initial dependencies.

Open `../../apps/varla-kol-collector` first. Start the KOL recorder and video center together with the floating Varla browser panel.

1. Run `Install_Environment.bat` to install dependencies.
2. Inside `KOL_recorder`, run `python create_blank_workbook.py` to create your blank tracker.
3. Return here and run `Start_Varla_Collector.bat`.
4. Leave both service windows running: KOL on 8765 and video center on 8766.
5. Load `chrome_extension`, open a target page, review the panel and record the data.

Local URL: `http://127.0.0.1:8766`

[Full program / browser-extension guide](../../apps/varla-kol-collector/README.en.md)

No real contacts or result workbooks are preloaded; initialize your own tracker first. Collection alone defaults to not-contacted; contacted status must be explicit.

### Instagram Current Metrics Core (`varla-instagram-monitor`)

Python 3.10+; local input processing uses the standard library, while sync needs separate configuration.

Open `../../apps/varla-instagram-monitor` first. Maintain current metrics and discovery/check timestamps by shortcode, then aggregate creators.

1. Collect real data first and prepare JSON using the record fields in the source.
2. Save discovery records to `data/discovery_input.json` and updates to `data/update_input.json`; create the data directory if needed.
3. Run `python main.py discover` followed by `python main.py update` here.
4. Run `python main.py sync` for a sync payload. Without sync_feishu.py, this exports locally rather than writing Feishu.

[Full program / browser-extension guide](../../apps/varla-instagram-monitor/README.en.md)

This core does not log in to or live-crawl Instagram by itself. Unavailable views must not become zero.

### KOL Recorder Chrome Extension (`kol-recorder-extension`)

Windows, Python 3.10+, Chrome/Edge and openpyxl.

Open `../../apps/kol-recorder-extension` first. Read visible Instagram/TikTok creator fields and write a local Excel tracker.

1. Open PowerShell here and run `python -m pip install -r requirements.txt`.
2. Run `python create_blank_workbook.py` to create a blank 16-column tracker only if none exists.
3. Run `start_kol_recorder.bat` and leave its service window open.
4. Load the extension below, open a creator profile, review parsed fields and record the result.

Local URL: `http://127.0.0.1:8765`

[Full program / browser-extension guide](../../apps/kol-recorder-extension/README.en.md)

Use only visible page data; hidden emails and unavailable metrics remain blank. Collection alone defaults to not-contacted; contacted status must be explicit.

### Varla Unified Collector Extension (`unified-collector-extension`)

Chrome/Edge plus the local services on ports 8765 and 8766.

Open `../../apps/unified-collector-extension` first. Switch between KOL records and video collection in one panel.

1. Start the full collector using `apps/varla-kol-collector/README.md` in the same bundle.
2. Alternatively run `start_varla_unified_collector.bat`, which looks for the sibling collector kit.
3. Load the extension below and check both backend statuses in its popup.
4. Open Instagram/TikTok/YouTube, use the Varla panel, review and save.

Local URL: `http://127.0.0.1:8766`

[Full program / browser-extension guide](../../apps/unified-collector-extension/README.en.md)

The browser extension is not a backend. Loading it without the collector cannot write Excel.

## 3. First task

| Prepare | Details |
| --- | --- |
| Input | Authorized creator/profile URLs and freshly collected metric JSON. |
| Output | Local workbooks, current SQLite metrics, creator summaries and Feishu sync payloads. |

```text
Use KOL视频抓取监控. Check collector services and input files, process only my three supplied posts, and produce local results before any Feishu write.
```


## Limits and troubleshooting

main.py reads input files. Running all does not prove a live crawl unless those inputs were freshly collected. Feishu writes require your configuration and a sync helper.

| Problem | Next step |
| --- | --- |
| Skill not visible | Check the installer output and destination SKILL.md, reopen Codex and start a new chat. |
| Program fails to start | Open its directory in PowerShell and run the documented command so the error remains visible; check that program's README. |
| Browser panel missing | Select the exact folder containing manifest.json, check supported websites and refresh the website tab. |
| External service unavailable | Supply your own authorization/settings and verify access. Keep local output rather than claiming a sync/send succeeded. |

## Privacy and status

This is a source/skill distribution. No real accounts, OAuth tokens, customer/KOL lists, contracts, orders, mailbox exports or business media are included. You configure your own services. Documentation and package paths were checked; live orders, sends and publications were not executed as part of documentation validation.

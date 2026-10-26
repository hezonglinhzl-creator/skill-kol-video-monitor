from __future__ import annotations

import html
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
import shutil
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
OUT_DIR = BASE_DIR / "outputs"
RESULT_XLSX = OUT_DIR / "一键电摩爆款视频搜索结果.xlsx"
RESULT_HTML = OUT_DIR / "一键电摩爆款视频搜索结果.html"
RESULT_MD = OUT_DIR / "一键电摩爆款视频_飞书导入.md"
HISTORY_DIR = OUT_DIR / "history"
AUTO_SCRIPT = BASE_DIR / "one_click_find_emoto_viral.py"
FEISHU_IMPORT = PROJECT_DIR / "公共脚本和缓存" / "scripts" / "feishu_import_markdown_tables.py"
PORT = 8766

HEADERS = [
    "序号",
    "平台",
    "视频链接",
    "标题/描述",
    "账号/来源",
    "点赞",
    "播放",
    "关键词",
    "爆火原因",
    "电摩改编方向",
    "优先级",
]

TASKS: dict[str, dict] = {
    "auto": {"running": False, "message": "未开始", "updated_at": ""},
    "feishu": {"running": False, "message": "未开始", "updated_at": ""},
}


def open_in_chrome(target: str) -> None:
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if chrome.exists():
        subprocess.Popen([str(chrome), target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        webbrowser.open(target)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def set_task(name: str, running: bool, message: str) -> None:
    TASKS[name] = {"running": running, "message": message, "updated_at": now()}


def compact(value: str, limit: int = 500) -> str:
    return re.sub(r"\s+", " ", value or "").strip()[:limit]


def load_auto_module():
    spec = importlib.util.spec_from_file_location("one_click_finder", AUTO_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def ensure_workbook() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if RESULT_XLSX.exists():
        normalize_workbook()
        return
    wb = Workbook()
    ws = wb.active
    ws.title = "A 级爆款视频"
    ws.append(HEADERS)
    fill = PatternFill("solid", fgColor="1F4E79")
    for cell in ws[1]:
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    widths = [8, 12, 50, 42, 20, 12, 12, 22, 72, 72, 10]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx)].width = width
    ws.freeze_panes = "A2"
    wb.save(RESULT_XLSX)


def normalize_workbook() -> None:
    wb = load_workbook(RESULT_XLSX)
    ws = wb.active
    if str(ws.cell(1, 1).value or "") != "序号":
        ws.insert_cols(1)
        ws.cell(1, 1).value = "序号"
    for row in range(2, ws.max_row + 1):
        ws.cell(row, 1).value = row - 1
    fill = PatternFill("solid", fgColor="1F4E79")
    for cell in ws[1]:
        cell.fill = fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    widths = [8, 12, 50, 42, 20, 12, 12, 22, 72, 72, 10]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx)].width = width
    wb.save(RESULT_XLSX)


def rows_from_xlsx(limit: int = 120) -> list[list[str]]:
    ensure_workbook()
    wb = load_workbook(RESULT_XLSX, data_only=True)
    ws = wb.active
    rows = []
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, limit + 1), values_only=True):
        rows.append([str(cell or "") for cell in row])
    return rows


def paged_rows_from_xlsx(page: int = 1, page_size: int = 20) -> dict:
    ensure_workbook()
    page = max(1, int(page or 1))
    page_size = max(5, min(100, int(page_size or 20)))
    wb = load_workbook(RESULT_XLSX, data_only=True)
    ws = wb.active
    headers = [str(cell.value or "") for cell in ws[1]]
    total = max(0, ws.max_row - 1)
    start = 2 + (page - 1) * page_size
    end = min(ws.max_row, start + page_size - 1)
    data_rows = []
    if start <= ws.max_row:
        for row in ws.iter_rows(min_row=start, max_row=end, values_only=True):
            data_rows.append([str(cell or "") for cell in row])
    return {
        "headers": headers,
        "rows": [headers] + data_rows,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


def save_history_snapshot(reason: str) -> None:
    if not RESULT_XLSX.exists():
        return
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_reason = re.sub(r"[^A-Za-z0-9_-]+", "_", reason or "snapshot").strip("_")[:40]
    target = HISTORY_DIR / f"{stamp}_{safe_reason}.xlsx"
    shutil.copy2(RESULT_XLSX, target)


def workbook_stats(path: Path) -> dict:
    try:
        wb = load_workbook(path, data_only=True)
        ws = wb.active
        total = max(0, ws.max_row - 1)
        links = []
        platforms = {}
        for row in range(2, ws.max_row + 1):
            platform = str(ws.cell(row, 2).value or "").strip()
            if platform:
                platforms[platform] = platforms.get(platform, 0) + 1
            value = str(ws.cell(row, 3).value or "").strip().rstrip("/")
            if value:
                links.append(value)
        return {
            "rows": total,
            "unique_links": len(set(links)),
            "duplicate_links": max(0, len(links) - len(set(links))),
            "platforms": platforms,
        }
    except Exception:
        return {"rows": 0, "unique_links": 0, "duplicate_links": 0, "platforms": {}}


def history_items() -> list[dict]:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for path in sorted(HISTORY_DIR.glob("*_50links.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)[:30]:
        stat = path.stat()
        stats = workbook_stats(path)
        items.append(
            {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                **stats,
            }
        )
    return items


def existing_urls(ws) -> set[str]:
    headers = [str(cell.value or "") for cell in ws[1]]
    link_col = headers.index("视频链接") + 1 if "视频链接" in headers else 3
    urls = set()
    for row in range(2, ws.max_row + 1):
        value = str(ws.cell(row, link_col).value or "").strip().rstrip("/")
        if value:
            urls.add(value)
    return urls


def platform_from_url(url: str) -> str:
    low = url.lower()
    if "tiktok.com" in low:
        return "TikTok"
    if "instagram.com" in low:
        return "Instagram"
    if "youtube.com" in low or "youtu.be" in low:
        return "YouTube"
    return "Other"


def account_from_url(url: str) -> str:
    patterns = [
        r"tiktok\.com/@([A-Za-z0-9._-]+)",
        r"instagram\.com/([A-Za-z0-9._-]+)/(?:reel|p|tv)",
        r"youtube\.com/@([A-Za-z0-9._-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url, re.I)
        if match:
            return "@" + match.group(1).lstrip("@")
    return ""


def fetch_title(url: str) -> str:
    oembed_urls = []
    if "youtube.com" in url.lower() or "youtu.be" in url.lower():
        oembed_urls.append("https://www.youtube.com/oembed?" + urllib.parse.urlencode({"url": url, "format": "json"}))
    if "tiktok.com" in url.lower():
        oembed_urls.append("https://www.tiktok.com/oembed?" + urllib.parse.urlencode({"url": url}))
    for api in oembed_urls:
        try:
            req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode("utf-8", errors="replace"))
            title = compact(data.get("title") or data.get("author_name") or "")
            if title:
                return title
        except Exception:
            pass
    return ""


def keyword_from_text(text: str) -> str:
    low = text.lower()
    for keyword in [
        "electric dirt bike",
        "emoto",
        "electric motorcycle",
        "electric moto",
        "surron",
        "talaria",
        "off road ebike",
        "electric ride",
        "bike check",
        "ride pov",
    ]:
        if keyword in low:
            return keyword
    return "manual link"


def append_link_rows(links: list[str]) -> dict:
    finder = load_auto_module()
    ensure_workbook()
    save_history_snapshot("before_manual_links")
    wb = load_workbook(RESULT_XLSX)
    ws = wb.active
    seen = existing_urls(ws)
    saved = 0
    duplicates = 0
    failed = 0

    for raw in links:
        url = raw.strip().split()[0].rstrip("/")
        if not url:
            continue
        if url in seen:
            duplicates += 1
            continue
        platform = platform_from_url(url)
        if platform == "Other":
            failed += 1
            continue
        title = fetch_title(url) or url
        keyword = keyword_from_text(" ".join([title, url]))
        account = account_from_url(url) or platform
        analysis_text = " ".join([title, account, url])
        reason, idea = finder.analyze(analysis_text, keyword, 0, 0)
        ws.append(
            [
                ws.max_row,
                platform,
                url,
                title,
                account,
                "",
                "",
                keyword,
                reason,
                idea,
                "A",
            ]
        )
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        seen.add(url)
        saved += 1

    wb.save(RESULT_XLSX)
    write_html_snapshot()
    return {"saved": saved, "duplicates": duplicates, "failed": failed}


def append_collected_items(items: list[dict]) -> dict:
    finder = load_auto_module()
    ensure_workbook()
    save_history_snapshot("before_plugin_collect")
    wb = load_workbook(RESULT_XLSX)
    ws = wb.active
    seen = existing_urls(ws)
    saved = 0
    duplicates = 0
    failed = 0
    errors = []

    for item in items:
        if not isinstance(item, dict):
            failed += 1
            continue
        url = str(item.get("url") or "").strip().rstrip("/")
        if not url:
            failed += 1
            continue
        if url in seen:
            duplicates += 1
            continue
        platform = str(item.get("platform") or platform_from_url(url))
        if platform == "Other":
            failed += 1
            continue
        title = compact(str(item.get("title") or item.get("body_text") or fetch_title(url) or url), 1000)
        account = str(item.get("account") or account_from_url(url) or platform)
        likes = str(item.get("likes") or "")
        views = str(item.get("views") or "")
        keyword = str(item.get("keyword") or keyword_from_text(" ".join([title, url])))
        analysis_text = " ".join(
            [
                title,
                str(item.get("body_text") or ""),
                account,
                url,
            ]
        )
        reason, idea = finder.analyze(analysis_text, keyword, finder.parse_count(views), finder.parse_count(likes))
        try:
            ws.append(
                [
                    ws.max_row,
                    platform,
                    url,
                    title,
                    account,
                    likes,
                    views,
                    keyword,
                    reason,
                    idea,
                    "A",
                ]
            )
            for cell in ws[ws.max_row]:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
            seen.add(url)
            saved += 1
        except Exception as exc:
            failed += 1
            errors.append(str(exc))

    wb.save(RESULT_XLSX)
    write_html_snapshot()
    return {"saved": saved, "duplicates": duplicates, "failed": failed, "errors": errors[:5]}


def reanalyze_existing_rows() -> dict:
    finder = load_auto_module()
    ensure_workbook()
    save_history_snapshot("before_reanalyze")
    wb = load_workbook(RESULT_XLSX)
    ws = wb.active
    headers = [str(cell.value or "") for cell in ws[1]]
    def col(name: str, fallback: int) -> int:
        return headers.index(name) + 1 if name in headers else fallback

    link_col = col("视频链接", 3)
    title_col = col("标题/描述", 4)
    account_col = col("账号/来源", 5)
    keyword_col = col("关键词", 8)
    reason_col = col("爆火原因", 9)
    idea_col = col("电摩改编方向", 10)
    views_col = col("播放", 7)
    changed = 0
    for row in range(2, ws.max_row + 1):
        title = str(ws.cell(row, title_col).value or "")
        link = str(ws.cell(row, link_col).value or "")
        account = str(ws.cell(row, account_col).value or "")
        keyword = str(ws.cell(row, keyword_col).value or "")
        views = finder.parse_count(str(ws.cell(row, views_col).value or ""))
        reason, idea = finder.analyze(" ".join([title, account, link]), keyword, views, 0)
        old_reason = str(ws.cell(row, reason_col).value or "")
        old_idea = str(ws.cell(row, idea_col).value or "")
        if reason != old_reason or idea != old_idea:
            ws.cell(row, reason_col).value = reason
            ws.cell(row, idea_col).value = idea
            changed += 1
    wb.save(RESULT_XLSX)
    write_html_snapshot()
    save_history_snapshot("after_reanalyze")
    return {"changed": changed}


def write_html_snapshot() -> None:
    rows = rows_from_xlsx(limit=500)
    table = []
    for ridx, row in enumerate(rows):
        tag = "th" if ridx == 0 else "td"
        cells = []
        for cidx, value in enumerate(row):
            if ridx > 0 and cidx == 2 and value:
                cells.append(f'<{tag}><a href="{html.escape(value)}" target="_blank">打开视频</a></{tag}>')
            else:
                cells.append(f"<{tag}>{html.escape(value)}</{tag}>")
        table.append("<tr>" + "".join(cells) + "</tr>")
    RESULT_HTML.write_text(
        f"""<!doctype html>
<meta charset="utf-8">
<title>一键电摩爆款视频搜索结果</title>
<style>
body{{font-family:Arial,'Microsoft YaHei',sans-serif;margin:24px;color:#1f2329}}
table{{border-collapse:collapse;width:1800px;font-size:13px;table-layout:fixed}}
th,td{{border:1px solid #d9dce3;padding:8px;vertical-align:top;word-break:break-word;line-height:1.45}}
th{{background:#d9eaf7}}
th:nth-child(9),td:nth-child(9),th:nth-child(10),td:nth-child(10){{width:330px}}
a{{color:#245bdb}}
</style>
<h1>一键电摩爆款视频搜索结果</h1>
<p>生成时间：{now()}</p>
<p>Excel 文件：{html.escape(str(RESULT_XLSX))}</p>
<table>{''.join(table)}</table>
""",
        encoding="utf-8",
    )


def run_auto_search_task() -> None:
    set_task("auto", True, "正在自动搜索 TikTok / Instagram / YouTube Shorts...")
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_xlsx = HISTORY_DIR / f"auto_search_{stamp}_50links.xlsx"
        run_html = HISTORY_DIR / f"auto_search_{stamp}_50links.html"
        env = os.environ.copy()
        env["VARLA_VIRAL_OUTPUT_XLSX"] = str(run_xlsx)
        env["VARLA_VIRAL_OUTPUT_HTML"] = str(run_html)
        result = subprocess.run(
            [sys.executable, str(AUTO_SCRIPT)],
            cwd=str(BASE_DIR),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=360,
        )
        message = result.stdout.strip()[-1200:] or "已完成"
        if result.returncode != 0:
            set_task("auto", False, "自动搜索失败：" + message)
            return
        if not run_xlsx.exists():
            set_task("auto", False, "自动搜索失败：没有生成新的结果文件。" + message)
            return
        stats = workbook_stats(run_xlsx)
        if stats["duplicate_links"]:
            set_task("auto", False, f"自动搜索失败：新表有 {stats['duplicate_links']} 个重复链接，已停止覆盖当前表。")
            return
        if stats["rows"] != 50 or stats["unique_links"] != 50:
            platforms = stats.get("platforms", {})
            set_task(
                "auto",
                False,
                f"自动搜索未达标：新表 {stats['rows']} 条，唯一链接 {stats['unique_links']} 条；平台分布 {platforms}；要求每份 50 条且不重复，已停止覆盖当前表。"
            )
            return
        shutil.copy2(run_xlsx, RESULT_XLSX)
        if run_html.exists():
            shutil.copy2(run_html, RESULT_HTML)
        set_task(
            "auto",
            False,
            f"自动搜索完成：新建 {run_xlsx.name}，共 {stats['rows']} 条，唯一链接 {stats['unique_links']} 条。\n" + message,
        )
    except Exception as exc:
        set_task("auto", False, f"自动搜索失败：{exc}")


def write_feishu_markdown() -> None:
    rows = rows_from_xlsx(limit=120)
    lines = ["# 外网爆款视频库", "", f"更新时间：{now()}", ""]
    if not rows:
        lines.append("暂无数据。")
    else:
        headers = rows[0]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in rows[1:]:
            clean = [str(cell).replace("\n", " ").replace("|", "/") for cell in row]
            lines.append("| " + " | ".join(clean) + " |")
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")


def run_feishu_task() -> None:
    set_task("feishu", True, "正在生成飞书表格文档...")
    try:
        write_feishu_markdown()
        if not FEISHU_IMPORT.exists():
            set_task("feishu", False, f"未找到飞书导入脚本：{FEISHU_IMPORT}")
            return
        result = subprocess.run(
            [sys.executable, str(FEISHU_IMPORT), str(RESULT_MD), "--title", "外网爆款视频库 - 电摩选题"],
            cwd=str(PROJECT_DIR),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=180,
        )
        set_task("feishu", False, result.stdout.strip()[-1500:] or "飞书同步完成")
    except Exception as exc:
        set_task("feishu", False, f"飞书同步失败：{exc}")


def start_chrome_debug() -> str:
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not chrome.exists():
        return "未找到 Chrome：C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    profile = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    subprocess.Popen(
        [
            str(chrome),
            "--remote-debugging-port=9222",
            "--profile-directory=Default",
            f"--user-data-dir={profile}",
            "https://www.instagram.com/explore/tags/ebike/",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return "已尝试打开 Chrome 调试窗口。如没有打开，请先手动关闭所有 Chrome 再点一次。"


def page() -> bytes:
    return f"""<!doctype html>
<meta charset="utf-8">
<title>爆款视频控制台</title>
<style>
  body {{ margin:0; font-family: Arial, "Microsoft YaHei", sans-serif; color:#1f2329; background:#f6f7f9; }}
  header {{ padding:22px 28px; background:#172033; color:white; }}
  h1 {{ margin:0; font-size:26px; }}
  main {{ padding:20px 28px; display:grid; gap:16px; }}
  section {{ background:white; border:1px solid #dfe3eb; border-radius:8px; padding:16px; }}
  h2 {{ margin:0 0 12px; font-size:18px; }}
  .row {{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
  button, a.button {{ border:0; border-radius:6px; padding:10px 14px; background:#245bdb; color:white; font-weight:700; cursor:pointer; text-decoration:none; display:inline-block; }}
  button.secondary {{ background:#43546f; }}
  button.ghost {{ background:#eef2ff; color:#245bdb; }}
  textarea {{ width:100%; min-height:100px; border:1px solid #ccd2df; border-radius:6px; padding:10px; font-size:13px; box-sizing:border-box; }}
  .status {{ white-space:pre-wrap; background:#f3f5f8; border:1px solid #dfe3eb; border-radius:6px; padding:10px; font-size:13px; }}
  .meta {{ color:#646a73; font-size:13px; }}
  table {{ border-collapse:collapse; width:100%; font-size:12px; table-layout:fixed; }}
  th,td {{ border:1px solid #dfe3eb; padding:7px; vertical-align:top; word-break:break-word; line-height:1.4; }}
  th {{ background:#e7f0fb; }}
  .table-wrap {{ overflow:auto; max-height:560px; }}
  code {{ background:#f1f3f6; padding:2px 4px; border-radius:4px; }}
</style>
<header>
  <h1>外网爆款视频控制台</h1>
  <div class="meta">自动搜索 / 链接投喂 / 分析入表 / 飞书同步，统一在这个本地网页里完成。</div>
</header>
<main>
  <section>
    <h2>1. 自动找爆款</h2>
    <div class="row">
      <button onclick="startAuto()">开始自动搜索</button>
      <button class="secondary" onclick="reanalyzeRows()">重新分析现有表格</button>
      <button class="secondary" onclick="openChrome()">打开已登录 Chrome 抓 INS</button>
      <a class="button ghost" href="/result-html" target="_blank">打开结果 HTML</a>
      <a class="button ghost" href="/xlsx" target="_blank">下载/打开 Excel</a>
    </div>
    <p class="meta">当前策略：TikTok 60%，Instagram 30%，YouTube Shorts 10%；YouTube 只收 Shorts。Instagram 公开抓不到时，需要用已登录 Chrome 页面/插件采集真实 Reels。</p>
    <div id="autoStatus" class="status">读取中...</div>
  </section>

  <section>
    <h2>2. 投喂链接给我分析</h2>
    <textarea id="links" placeholder="每行一个 TikTok / Instagram Reel / YouTube Shorts 链接"></textarea>
    <div class="row">
      <button onclick="analyzeLinks()">分析并写入表格</button>
      <button class="ghost" onclick="refreshRecords()">刷新表格</button>
    </div>
    <div id="linkStatus" class="status">等待链接。</div>
  </section>

  <section>
    <h2>3. 同步到飞书</h2>
    <div class="row">
      <button onclick="syncFeishu()">生成飞书原生表格文档</button>
      <a class="button ghost" href="/md" target="_blank">查看飞书 Markdown</a>
    </div>
    <p class="meta">如果指定 Wiki 权限没开，默认创建新的飞书文档；拿到权限后再改成写指定 Wiki。</p>
    <div id="feishuStatus" class="status">读取中...</div>
  </section>

  <section>
    <h2>4. 已采集表格预览</h2>
    <div class="row">
      <button class="ghost" onclick="prevPage()">上一页</button>
      <span id="pageInfo" class="meta">第 1 页</span>
      <button class="ghost" onclick="nextPage()">下一页</button>
      <select id="pageSize" onchange="changePageSize()">
        <option value="10">每页 10 条</option>
        <option value="20" selected>每页 20 条</option>
        <option value="50">每页 50 条</option>
      </select>
    </div>
    <div class="table-wrap" id="records">加载中...</div>
  </section>

  <section>
    <h2>5. 历史记录</h2>
    <p class="meta">每次自动搜索或投喂链接前后会自动保存 Excel 快照，方便回退和对比。</p>
    <div id="history" class="status">加载中...</div>
  </section>
</main>
<script>
let currentPage = 1;
let totalPages = 1;
async function api(path, options) {{
  const res = await fetch(path, options);
  return await res.json();
}}
async function refreshStatus() {{
  try {{
    const data = await api('/api/status');
    autoStatus.textContent = data.auto.message + '\\n更新时间：' + data.auto.updated_at;
    feishuStatus.textContent = data.feishu.message + '\\n更新时间：' + data.feishu.updated_at;
  }} catch (err) {{
    autoStatus.textContent = '状态刷新失败：' + err.message;
  }}
}}
async function startAuto() {{
  autoStatus.textContent = '已提交任务，正在开始...';
  await api('/api/start-auto', {{method:'POST'}});
  setTimeout(refreshLoop, 800);
}}
async function openChrome() {{
  const data = await api('/api/open-chrome', {{method:'POST'}});
  autoStatus.textContent = data.message;
}}
async function analyzeLinks() {{
  const lines = links.value.split(/\\n+/).map(x => x.trim()).filter(Boolean);
  linkStatus.textContent = '正在分析 ' + lines.length + ' 个链接...';
  const data = await api('/api/analyze-links', {{
    method:'POST',
    headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{links:lines}})
  }});
  linkStatus.textContent = JSON.stringify(data, null, 2);
  await refreshRecords();
}}
async function syncFeishu() {{
  feishuStatus.textContent = '已提交飞书同步任务...';
  await api('/api/sync-feishu', {{method:'POST'}});
  setTimeout(refreshLoop, 800);
}}
async function reanalyzeRows() {{
  autoStatus.textContent = '正在按新规则重新分析现有表格...';
  const data = await api('/api/reanalyze', {{method:'POST'}});
  autoStatus.textContent = JSON.stringify(data, null, 2);
  await refreshRecords();
  await refreshHistory();
}}
function renderTable(rows) {{
  if (!rows.length) return '暂无数据';
  return '<table>' + rows.map((row, i) => '<tr>' + row.map((cell, c) => {{
    const tag = i === 0 ? 'th' : 'td';
    if (i > 0 && c === 2 && cell) return `<${{tag}}><a href="${{cell}}" target="_blank">打开视频</a></${{tag}}>`;
    return `<${{tag}}>${{String(cell).replace(/[&<>]/g, s => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[s]))}}</${{tag}}>`;
  }}).join('') + '</tr>').join('') + '</table>';
}}
async function refreshRecords() {{
  try {{
    const size = document.getElementById('pageSize').value || 20;
    const data = await api(`/api/records?page=${{currentPage}}&page_size=${{size}}`);
    currentPage = data.page || 1;
    totalPages = data.pages || 1;
    pageInfo.textContent = `第 ${{currentPage}} / ${{totalPages}} 页，共 ${{data.total || 0}} 条`;
    records.innerHTML = renderTable(data.rows || []);
  }} catch (err) {{
    records.textContent = '表格刷新失败：' + err.message;
  }}
}}
async function refreshHistory() {{
  try {{
    const data = await api('/api/history');
    const items = data.items || [];
    history.innerHTML = items.length
      ? items.map(x => `${{x.time}} ｜ ${{x.rows}} 条 ｜ 唯一链接 ${{x.unique_links}} ｜ 重复 ${{x.duplicate_links}} ｜ ${{x.name}}`).join('<br>')
      : '暂无历史记录';
  }} catch (err) {{
    history.textContent = '历史记录刷新失败：' + err.message;
  }}
}}
function prevPage() {{
  currentPage = Math.max(1, currentPage - 1);
  refreshRecords();
}}
function nextPage() {{
  currentPage = Math.min(totalPages, currentPage + 1);
  refreshRecords();
}}
function changePageSize() {{
  currentPage = 1;
  refreshRecords();
}}
async function refreshLoop() {{
  await Promise.all([refreshStatus(), refreshRecords(), refreshHistory()]);
  setTimeout(refreshLoop, 3000);
}}
refreshLoop();
</script>
""".encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def send_json(self, data: dict, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page())
            return
        if parsed.path == "/health":
            self.send_json({"ok": True, "service": "viral_video_control_center"})
            return
        if parsed.path == "/api/status":
            self.send_json({"auto": TASKS["auto"], "feishu": TASKS["feishu"]})
            return
        if parsed.path == "/api/records":
            params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
            self.send_json(paged_rows_from_xlsx(params.get("page", 1), params.get("page_size", 20)))
            return
        if parsed.path == "/api/history":
            self.send_json({"items": history_items()})
            return
        if parsed.path == "/result-html":
            write_html_snapshot()
            open_in_chrome(RESULT_HTML.as_uri())
            self.send_response(302)
            self.send_header("Location", RESULT_HTML.as_uri())
            self.end_headers()
            return
        if parsed.path == "/xlsx":
            open_in_chrome(RESULT_XLSX.as_uri())
            self.send_json({"path": str(RESULT_XLSX)})
            return
        if parsed.path == "/md":
            write_feishu_markdown()
            open_in_chrome(RESULT_MD.as_uri())
            self.send_json({"path": str(RESULT_MD)})
            return
        if parsed.path == "/add":
            params = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
            result = append_collected_items([params])
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                f"""<!doctype html><meta charset="utf-8">
<style>body{{font-family:Arial,'Microsoft YaHei',sans-serif;margin:40px}}</style>
<h2>采集完成</h2>
<p>新增：{result.get('saved', 0)}，重复：{result.get('duplicates', 0)}，失败：{result.get('failed', 0)}</p>
<p>可以关闭本页，继续采集下一个。</p>""".encode("utf-8")
            )
            return
        self.send_json({"error": "not found"}, status=404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/start-auto":
            if not TASKS["auto"]["running"]:
                threading.Thread(target=run_auto_search_task, daemon=True).start()
            self.send_json({"ok": True, "task": TASKS["auto"]})
            return
        if parsed.path == "/api/open-chrome":
            self.send_json({"ok": True, "message": start_chrome_debug()})
            return
        if parsed.path == "/api/analyze-links":
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8", errors="replace") or "{}")
            result = append_link_rows(payload.get("links") or [])
            self.send_json({"ok": True, **result})
            return
        if parsed.path == "/bulk":
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8", errors="replace") or "{}")
            result = append_collected_items(payload.get("items") or [])
            self.send_json({"ok": True, **result})
            return
        if parsed.path == "/api/sync-feishu":
            if not TASKS["feishu"]["running"]:
                threading.Thread(target=run_feishu_task, daemon=True).start()
            self.send_json({"ok": True, "task": TASKS["feishu"]})
            return
        if parsed.path == "/api/reanalyze":
            result = reanalyze_existing_rows()
            self.send_json({"ok": True, **result})
            return
        self.send_json({"error": "not found"}, status=404)

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    ensure_workbook()
    write_html_snapshot()
    url = f"http://127.0.0.1:{PORT}"
    print(f"Viral video control center: {url}")
    print(f"Workbook: {RESULT_XLSX}")
    open_in_chrome(url)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

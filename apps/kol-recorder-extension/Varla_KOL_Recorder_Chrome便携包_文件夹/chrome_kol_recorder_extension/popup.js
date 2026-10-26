const serverEl = document.getElementById("server");
const tabEl = document.getElementById("tab");
const button = document.getElementById("record");
const scrapeBox = document.getElementById("scrape");

let currentTab = null;
let serverOk = false;

async function getCurrentTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  return tabs[0];
}

function isKolPage(url) {
  if (!url) return false;
  if (url.includes("127.0.0.1") || url.includes("localhost")) return false;
  try {
    const u = new URL(url);
    const host = u.hostname.toLowerCase();
    const path = u.pathname.replace(/\/$/, "");
    if (host.includes("tiktok.com")) return /^\/@[^/]+$/.test(path);
    if (host.includes("instagram.com")) {
      const username = path.split("/").filter(Boolean)[0] || "";
      return /^\/[^/]+$/.test(path) && !["p", "reel", "reels", "stories", "explore", "accounts", "direct"].includes(username);
    }
  } catch {}
  return false;
}

async function checkServer() {
  try {
    const res = await fetch("http://127.0.0.1:8765/health", { cache: "no-store" });
    serverOk = res.ok;
  } catch {
    serverOk = false;
  }
  serverEl.className = "status " + (serverOk ? "ok" : "bad");
  serverEl.textContent = serverOk ? "后台已连接" : "后台未启动：请先双击 start_kol_recorder.bat";
}

async function refresh() {
  currentTab = await getCurrentTab();
  const url = currentTab?.url || "";
  tabEl.textContent = currentTab ? `${currentTab.title || ""}\n${url}` : "没有读取到当前标签页";
  await checkServer();
  button.disabled = !(serverOk && isKolPage(url));
  if (!isKolPage(url)) {
    tabEl.textContent += "\n\n请打开 TikTok 或 Instagram 的 KOL 账号主页，不要在搜索页/视频页/记录结果页点击。";
  }
}

button.addEventListener("click", async () => {
  if (!currentTab) return;
  const url = encodeURIComponent(currentTab.url || "");
  const title = encodeURIComponent(currentTab.title || "");
  let extra = "";

  if (scrapeBox.checked) {
    try {
      const [result] = await chrome.scripting.executeScript({
        target: { tabId: currentTab.id },
        func: scrapeVisibleKolData
      });
      const data = result?.result || {};
      for (const [key, value] of Object.entries(data)) {
        if (value !== undefined && value !== null && String(value).trim()) {
          extra += `&${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`;
        }
      }
    } catch (err) {
      console.warn("KOL data scrape failed", err);
    }
  }

  const target = `http://127.0.0.1:8765/add?url=${url}&title=${title}${extra}`;
  await chrome.tabs.create({ url: target });
});

refresh();

function scrapeVisibleKolData() {
  const bodyText = document.body?.innerText || "";

  function parseCompactNumber(text) {
    if (!text) return null;
    const raw = String(text).replace(/,/g, "").trim();
    const match = raw.match(/(\d+(?:\.\d+)?)\s*([KMB万亿]?)/i);
    if (!match) return null;
    let n = Number(match[1]);
    const unit = match[2]?.toUpperCase();
    if (unit === "K") n *= 1_000;
    if (unit === "M") n *= 1_000_000;
    if (unit === "B") n *= 1_000_000_000;
    if (unit === "万") n *= 10_000;
    if (unit === "亿") n *= 100_000_000;
    return Math.round(n);
  }

  function formatNumber(n) {
    if (!Number.isFinite(n)) return "";
    const abs = Math.abs(n);
    if (abs >= 1_000_000) return (n / 1_000_000).toFixed(abs >= 10_000_000 ? 1 : 1).replace(/\.0$/, "") + "M";
    if (abs >= 1_000) return (n / 1_000).toFixed(abs >= 100_000 ? 0 : 1).replace(/\.0$/, "") + "K";
    return String(Math.round(n));
  }

  const emailMatch = bodyText.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  const followersMatch = bodyText.match(/([\d,.]+(?:\.\d+)?\s*[KMB万亿]?)\s*Followers/i)
    || bodyText.match(/Followers\s*([\d,.]+(?:\.\d+)?\s*[KMB万亿]?)/i);
  const followers = followersMatch ? parseCompactNumber(followersMatch[1]) : null;

  const countryAliases = [
    ["United States", ["United States", "USA", "US", "美国"]],
    ["Canada", ["Canada", "加拿大"]],
    ["United Kingdom", ["United Kingdom", "UK", "英国"]],
    ["Germany", ["Germany", "德国"]],
    ["France", ["France", "法国"]],
    ["Italy", ["Italy", "意大利"]],
    ["Spain", ["Spain", "西班牙"]],
    ["Australia", ["Australia", "澳大利亚"]],
    ["Netherlands", ["Netherlands", "荷兰"]],
    ["Mexico", ["Mexico", "墨西哥"]],
    ["Brazil", ["Brazil", "巴西"]],
    ["Japan", ["Japan", "日本"]],
    ["Korea", ["Korea", "韩国"]],
    ["Singapore", ["Singapore", "新加坡"]]
  ];
  let country = "";
  for (const [standard, aliases] of countryAliases) {
    if (aliases.some(alias => bodyText.includes(alias))) {
      country = standard;
      break;
    }
  }

  // Prefer visible video-card numbers. This works with TikTok and many analytics overlays,
  // including EchoTik-style cards where view counts appear as compact numbers on thumbnails.
  const candidates = [];
  const elements = Array.from(document.querySelectorAll("span,strong,div,p"));
  for (const el of elements) {
    const text = (el.innerText || "").trim();
    if (!/^\d+(?:\.\d+)?\s*[KMB万亿]?$/.test(text.replace(/,/g, ""))) continue;
    const n = parseCompactNumber(text);
    if (!n || n < 100) continue;
    const rect = el.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) continue;
    candidates.push({ n, top: rect.top, left: rect.left, text });
  }

  // Remove likely profile counters from the top profile area, then keep visible video counts.
  const videoNums = candidates
    .filter(x => x.top > 430)
    .map(x => x.n)
    .filter(n => !(followers && Math.abs(n - followers) < 2));

  const deduped = [];
  for (const n of videoNums) {
    if (!deduped.includes(n)) deduped.push(n);
  }
  const firstTen = deduped.slice(0, 10);
  const avgViews = firstTen.length ? Math.round(firstTen.reduce((a, b) => a + b, 0) / firstTen.length) : "";
  const bestVideoViews = firstTen.length ? Math.max(...firstTen) : "";

  const lower = bodyText.toLowerCase();
  let contentType = "";
  if (/moto|dirt bike|surron|sur ron|talaria|rider|helmet|bike/.test(lower)) contentType = "Moto";
  else if (/e-bike|ebike|scooter|pev/.test(lower)) contentType = "PEV";
  else if (/camp|outdoor|trail|farm|backyard/.test(lower)) contentType = "Outdoor";
  else if (/family|kid|kids|dad|mom/.test(lower)) contentType = "Family";
  else if (/review|unbox|ugc/.test(lower)) contentType = "UGC";

  return {
    email: emailMatch ? emailMatch[0] : "",
    country,
    followers: formatNumber(followers),
    avg_views: formatNumber(avgViews),
    best_video_views: formatNumber(bestVideoViews),
    content_type: contentType
  };
}

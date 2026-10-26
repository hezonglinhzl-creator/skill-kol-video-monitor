(function () {
  if (window.__kolRecorderFloatingInjected) return;
  window.__kolRecorderFloatingInjected = true;

  const SERVER = "http://127.0.0.1:8765";

  function isKolProfileUrl(url) {
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

  function platformFromUrl(url) {
    const low = (url || "").toLowerCase();
    if (low.includes("tiktok.com")) return "TK";
    if (low.includes("instagram.com")) return "Instagram";
    return "";
  }

  function handleFromUrl(url) {
    const patterns = [
      /tiktok\.com\/@([^/?#]+)/i,
      /instagram\.com\/([^/?#]+)/i
    ];
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return "@" + match[1].replace(/^@/, "");
    }
    return "";
  }

  function parseCompactNumber(text) {
    if (!text) return null;
    const raw = String(text).replace(/,/g, "").trim();
    const match = raw.match(/(\d+(?:\.\d+)?)\s*([KMB万亿]?)/i);
    if (!match) return null;
    let n = Number(match[1]);
    const unit = (match[2] || "").toUpperCase();
    if (unit === "K") n *= 1000;
    if (unit === "M") n *= 1000000;
    if (unit === "B") n *= 1000000000;
    if (unit === "万") n *= 10000;
    if (unit === "亿") n *= 100000000;
    return Number.isFinite(n) ? Math.round(n) : null;
  }

  function formatNumber(n) {
    if (!Number.isFinite(n)) return "";
    if (n >= 1000000) return (n / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
    if (n >= 1000) return (n / 1000).toFixed(n >= 100000 ? 0 : 1).replace(/\.0$/, "") + "K";
    return String(Math.round(n));
  }

  function scrapeKolData() {
    const bodyText = document.body?.innerText || "";
    const url = location.href.split("?")[0].replace(/\/$/, "");
    const title = document.title || "";

    const emailMatch = bodyText.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
    const followersMatch =
      bodyText.match(/([\d,.]+(?:\.\d+)?\s*[KMB万亿]?)\s*Followers/i) ||
      bodyText.match(/Followers\s*([\d,.]+(?:\.\d+)?\s*[KMB万亿]?)/i) ||
      bodyText.match(/粉丝\s*([\d,.]+(?:\.\d+)?\s*[KMB万亿]?)/i);
    const followers = followersMatch ? parseCompactNumber(followersMatch[1]) : null;

    const countryAliases = [
      ["United States", ["United States", "USA", "US", "美国"]],
      ["Canada", ["Canada", "加拿大"]],
      ["United Kingdom", ["United Kingdom", "UK", "英国"]],
      ["Germany", ["Germany", "德国"]],
      ["France", ["France", "法国"]],
      ["Australia", ["Australia", "澳大利亚"]],
      ["Mexico", ["Mexico", "墨西哥"]]
    ];
    let country = "";
    for (const [standard, aliases] of countryAliases) {
      if (aliases.some(alias => bodyText.includes(alias))) {
        country = standard;
        break;
      }
    }

    const lower = bodyText.toLowerCase();
    let contentType = "";
    if (/moto|dirt bike|surron|sur ron|talaria|rider|helmet|bike/.test(lower)) contentType = "Moto";
    else if (/e-bike|ebike|scooter|pev/.test(lower)) contentType = "PEV";
    else if (/camp|outdoor|trail|farm|backyard/.test(lower)) contentType = "Outdoor";
    else if (/family|kid|kids|dad|mom/.test(lower)) contentType = "Family";
    else if (/review|unbox|ugc/.test(lower)) contentType = "UGC";

    const nums = [];
    for (const el of Array.from(document.querySelectorAll("span,strong,div,p"))) {
      const text = (el.innerText || "").trim();
      if (!/^\d+(?:\.\d+)?\s*[KMB万亿]?$/.test(text.replace(/,/g, ""))) continue;
      const n = parseCompactNumber(text);
      if (!n || n < 100) continue;
      const rect = el.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0 || rect.top < 360) continue;
      nums.push(n);
    }
    const deduped = [];
    for (const n of nums) {
      if (!deduped.includes(n)) deduped.push(n);
    }
    const firstTen = deduped.slice(0, 10);
    const avgViews = firstTen.length ? Math.round(firstTen.reduce((a, b) => a + b, 0) / firstTen.length) : "";
    const bestVideoViews = firstTen.length ? Math.max(...firstTen) : "";

    return {
      url,
      title,
      platform: platformFromUrl(url),
      handle: handleFromUrl(url),
      email: emailMatch ? emailMatch[0] : "",
      country,
      followers: formatNumber(followers),
      avg_views: formatNumber(avgViews),
      best_video_views: formatNumber(bestVideoViews),
      content_type: contentType
    };
  }

  async function checkServer() {
    try {
      const res = await fetch(`${SERVER}/health`, { cache: "no-store" });
      return res.ok;
    } catch {
      return false;
    }
  }

  function setStatus(text, ok = true) {
    const el = document.getElementById("kol-recorder-status");
    if (!el) return;
    el.textContent = text;
    el.style.color = ok ? "#0f7b3f" : "#b42318";
  }

  function queryFromData(data) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(data)) {
      if (value !== undefined && value !== null && String(value).trim()) {
        params.set(key, String(value));
      }
    }
    return params.toString();
  }

  async function recordKol() {
    const ok = await checkServer();
    if (!ok) return setStatus("本地服务未启动", false);
    if (!isKolProfileUrl(location.href)) return setStatus("当前不是 KOL 主页", false);
    const data = scrapeKolData();
    try {
      const res = await fetch(`${SERVER}/add?${queryFromData(data)}`, { cache: "no-store" });
      const text = await res.text();
      if (res.ok && /已记录|宸茶/.test(text)) {
        setStatus(`已记录 ${data.handle || ""}`);
      } else {
        setStatus("已请求记录，请检查台账", true);
      }
    } catch (err) {
      setStatus(`记录失败：${err.message}`, false);
    }
  }

  function makeButton(text, onClick) {
    const btn = document.createElement("button");
    btn.textContent = text;
    btn.style.cssText = "border:0;border-radius:6px;padding:8px 9px;background:#245bdb;color:white;font-weight:800;cursor:pointer;font-size:12px;";
    btn.addEventListener("click", onClick);
    return btn;
  }

  function injectPanel() {
    const existing = document.getElementById("kol-recorder-panel");
    if (existing) existing.remove();
    if (!/tiktok\.com|instagram\.com/i.test(location.hostname)) return;

    const panel = document.createElement("div");
    panel.id = "kol-recorder-panel";
    panel.style.cssText = [
      "position:fixed",
      "right:18px",
      "top:96px",
      "z-index:2147483647",
      "width:164px",
      "background:white",
      "border:1px solid #ccd2df",
      "box-shadow:0 8px 28px rgba(0,0,0,.18)",
      "border-radius:8px",
      "padding:10px",
      "font-family:Arial,'Microsoft YaHei',sans-serif",
      "color:#1f2329"
    ].join(";");

    const close = document.createElement("button");
    close.textContent = "×";
    close.style.cssText = "position:absolute;right:6px;top:5px;border:0;background:transparent;color:#646a73;font-size:16px;cursor:pointer;";
    close.addEventListener("click", () => panel.remove());

    const title = document.createElement("div");
    title.textContent = "KOL记录器";
    title.style.cssText = "font-weight:900;font-size:14px;margin-bottom:7px;";

    const status = document.createElement("div");
    status.id = "kol-recorder-status";
    status.textContent = "检测服务中...";
    status.style.cssText = "font-size:12px;line-height:1.35;margin:6px 0;color:#646a73;";

    const button = makeButton("记录当前KOL", recordKol);
    const open = makeButton("打开台账", () => window.open(SERVER, "_blank"));
    open.style.background = "#43546f";

    panel.appendChild(close);
    panel.appendChild(title);
    panel.appendChild(status);
    panel.appendChild(button);
    panel.appendChild(document.createElement("div")).style.height = "7px";
    panel.appendChild(open);
    document.body.appendChild(panel);

    checkServer().then(ok => {
      if (!ok) return setStatus("本地服务未启动", false);
      setStatus(isKolProfileUrl(location.href) ? "可记录当前主页" : "请打开账号主页", isKolProfileUrl(location.href));
    });
  }

  injectPanel();
  let lastHref = location.href;
  setInterval(() => {
    if (location.href !== lastHref) {
      lastHref = location.href;
      setTimeout(injectPanel, 800);
    }
  }, 1000);
})();

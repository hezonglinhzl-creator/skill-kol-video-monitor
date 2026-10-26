(function () {
  if (window.__varlaUnifiedCollectorInjected) return;
  window.__varlaUnifiedCollectorInjected = true;

  const VIDEO_SERVER = "http://127.0.0.1:8766";
  const KOL_SERVER = "http://127.0.0.1:8765";
  const PANEL_POS_KEY = "varlaUnifiedPanelPosition";

  const T = {
    title: "Varla\u91c7\u96c6",
    recordKol: "\u8bb0\u5f55\u5f53\u524dKOL",
    collectVideo: "\u91c7\u96c6\u5f53\u524d\u89c6\u9891",
    collectReels: "\u91c7\u96c6\u672c\u9875Reels",
    viralHub: "\u7206\u6b3e\u63a7\u5236\u53f0",
    kolLedger: "KOL\u53f0\u8d26",
    kolNotPage: "\u5f53\u524d\u4e0d\u662fKOL\u4e3b\u9875",
    videoNotPage: "\u5f53\u524d\u4e0d\u662f\u89c6\u9891\u9875",
    reelsNotFound: "\u6ca1\u627e\u5230\u53ef\u89c1Reels\uff0c\u5148\u6eda\u52a8\u9875\u9762",
    kolServerOff: "KOL\u670d\u52a1\u672a\u542f\u52a8",
    viralServerOff: "\u7206\u6b3e\u670d\u52a1\u672a\u542f\u52a8"
  };

  function cleanUrl(url) {
    try {
      const u = new URL(String(url || ""), location.href);
      return `${u.origin}${u.pathname.replace(/\/$/, "")}`;
    } catch {
      return String(url || "").split("?")[0].replace(/\/$/, "");
    }
  }

  function pageText() {
    return document.body?.innerText || "";
  }

  function profileTextOnly() {
    return document.querySelector("main")?.innerText || pageText();
  }

  function platformFromUrl(url) {
    const low = String(url || "").toLowerCase();
    if (low.includes("tiktok.com")) return "TikTok";
    if (low.includes("instagram.com")) return "Instagram";
    if (low.includes("youtube.com") || low.includes("youtu.be")) return "YouTube";
    return "";
  }

  function kolPlatformFromUrl(url) {
    const platform = platformFromUrl(url);
    return platform === "TikTok" ? "TK" : platform;
  }

  function instagramUsernameFromPath(pathname) {
    return String(pathname || "").split("/").filter(Boolean)[0] || "";
  }

  function instagramProfileUrl(url) {
    try {
      const u = new URL(url);
      if (!u.hostname.toLowerCase().includes("instagram.com")) return cleanUrl(url);
      const username = instagramUsernameFromPath(u.pathname);
      return username ? `${u.origin}/${username}` : cleanUrl(url);
    } catch {
      return cleanUrl(url);
    }
  }

  function youtubeChannelUrl(url) {
    try {
      const u = new URL(url);
      if (!u.hostname.toLowerCase().includes("youtube.com")) return cleanUrl(url);
      const parts = u.pathname.split("/").filter(Boolean);
      if (!parts.length) return cleanUrl(url);
      if (parts[0].startsWith("@")) return `${u.origin}/${parts[0]}`;
      if (["channel", "c", "user"].includes(parts[0]) && parts[1]) return `${u.origin}/${parts[0]}/${parts[1]}`;
      return cleanUrl(url);
    } catch {
      return cleanUrl(url);
    }
  }

  function profileUrlForRecord(url) {
    const low = String(url || "").toLowerCase();
    if (low.includes("instagram.com")) return instagramProfileUrl(url);
    if (low.includes("youtube.com")) return youtubeChannelUrl(url);
    return cleanUrl(url);
  }

  function isKolProfileUrl(url) {
    try {
      const u = new URL(url);
      const host = u.hostname.toLowerCase();
      const path = u.pathname.replace(/\/$/, "");
      if (host.includes("tiktok.com")) return /^\/@[^/]+$/.test(path);
      if (host.includes("instagram.com")) {
        const parts = path.split("/").filter(Boolean);
        const username = parts[0] || "";
        if (!username || ["p", "reel", "stories", "explore", "accounts", "direct"].includes(username)) return false;
        return parts.length === 1 || (parts.length === 2 && ["reels", "tagged"].includes(parts[1]));
      }
      if (host.includes("youtube.com")) {
        const parts = path.split("/").filter(Boolean);
        if (!parts.length) return false;
        if (["watch", "shorts", "feed", "results", "playlist"].includes(parts[0])) return false;
        if (parts[0].startsWith("@")) return parts.length === 1 || (parts.length === 2 && ["videos", "shorts", "featured", "about"].includes(parts[1]));
        if (["channel", "c", "user"].includes(parts[0]) && parts[1]) return parts.length === 2 || (parts.length === 3 && ["videos", "shorts", "featured", "about"].includes(parts[2]));
      }
    } catch {}
    return false;
  }

  function isVideoUrl(url) {
    try {
      const u = new URL(url);
      const host = u.hostname.toLowerCase();
      const path = u.pathname.toLowerCase();
      if (host.includes("tiktok.com")) return /\/@[^/]+\/video\//.test(path) || /\/t\//.test(path);
      if (host.includes("instagram.com")) return /\/reel\//.test(path) || /\/p\//.test(path);
      if (host.includes("youtube.com")) return path.startsWith("/shorts/") || (path === "/watch" && u.searchParams.has("v"));
      if (host.includes("youtu.be")) return true;
    } catch {}
    return false;
  }

  function handleFromUrl(url) {
    const patterns = [
      /tiktok\.com\/@([^/?#]+)/i,
      /instagram\.com\/([^/?#]+)/i,
      /youtube\.com\/@([^/?#]+)/i,
      /youtube\.com\/(?:channel|c|user)\/([^/?#]+)/i
    ];
    for (const pattern of patterns) {
      const match = String(url || "").match(pattern);
      if (match) return "@" + match[1].replace(/^@/, "");
    }
    return "";
  }

  function youtubeDisplayName(text, handle) {
    const rawHandle = String(handle || "").replace(/^@/, "");
    const title = String(document.title || "")
      .replace(/\s*-\s*YouTube\s*$/i, "")
      .replace(/\s*-\s*YouTube.*$/i, "")
      .trim();
    if (title && title.toLowerCase() !== "youtube") return title.slice(0, 80);
    const lines = String(text || "")
      .split(/\n+/)
      .map(line => line.trim())
      .filter(Boolean)
      .filter(line => line.toLowerCase() !== rawHandle.toLowerCase())
      .filter(line => !/^(home|videos|shorts|live|playlists|community|channels|about|subscribe|subscribed)$/i.test(line))
      .filter(line => !/^\d/.test(line));
    return lines[0] || rawHandle || handle || "";
  }

  function isInstagramProfileSubpage(url) {
    try {
      const u = new URL(url);
      if (!u.hostname.toLowerCase().includes("instagram.com")) return false;
      const parts = u.pathname.replace(/\/$/, "").split("/").filter(Boolean);
      return parts.length === 2 && ["reels", "tagged"].includes(parts[1]);
    } catch {
      return false;
    }
  }

  function parseCompactNumber(text) {
    if (!text) return null;
    const raw = String(text).replace(/,/g, "").trim();
    const match = raw.match(/(\d+(?:\.\d+)?)\s*([KMBkmb\u4e07\u4ebf]?)/);
    if (!match) return null;
    let n = Number(match[1]);
    const unit = match[2] || "";
    if (/k/i.test(unit)) n *= 1000;
    if (/m/i.test(unit)) n *= 1000000;
    if (/b/i.test(unit)) n *= 1000000000;
    if (unit === "\u4e07") n *= 10000;
    if (unit === "\u4ebf") n *= 100000000;
    return Number.isFinite(n) ? Math.round(n) : null;
  }

  function formatNumber(n) {
    if (!Number.isFinite(n)) return "";
    if (n >= 1000000) return (n / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
    if (n >= 1000) return (n / 1000).toFixed(n >= 100000 ? 0 : 1).replace(/\.0$/, "") + "K";
    return String(Math.round(n));
  }

  function extractNumbers(text) {
    const values = [];
    const pattern = /(\d+(?:[,.]\d+)*(?:\.\d+)?)\s*([KMBkmb\u4e07\u4ebf]?)/g;
    for (const match of String(text || "").matchAll(pattern)) {
      const value = parseCompactNumber(`${match[1]}${match[2] || ""}`);
      if (Number.isFinite(value)) values.push(value);
    }
    return values;
  }

  function avgNumber(values) {
    const nums = values.filter(Number.isFinite);
    if (!nums.length) return null;
    return Math.round(nums.reduce((sum, n) => sum + n, 0) / nums.length);
  }

  function visibleInstagramPostStats() {
    const stats = [];
    const seen = new Set();
    const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]'));
    const viewsWords = "(?:views|plays|play|\\u64ad\\u653e|\\u89c2\\u770b|\\u6b21\\u64ad\\u653e|\\u6b21\\u89c2\\u770b)";
    const viewsPattern = new RegExp(`(\\d+(?:[,.]\\d+)*(?:\\.\\d+)?\\s*[KMBkmb\\u4e07\\u4ebf]?)\\s*${viewsWords}`, "i");

    for (const a of anchors) {
      const href = cleanUrl(new URL(a.getAttribute("href"), location.origin).href);
      if (seen.has(href)) continue;
      seen.add(href);

      let card = a;
      for (let i = 0; i < 6 && card && (card.innerText || "").length < 8; i += 1) {
        card = card.parentElement;
      }
      const text = [
        card?.innerText || "",
        a.getAttribute("aria-label") || "",
        a.querySelector("img")?.getAttribute("alt") || "",
        a.parentElement?.innerText || ""
      ].join("\n");

      const match = text.match(viewsPattern);
      if (match) {
        stats.push({ href, value: parseCompactNumber(match[1]) });
      } else if (isInstagramProfileSubpage(location.href)) {
        const numbers = extractNumbers(text)
          .filter(n => Number.isFinite(n))
          .filter(n => n >= 100);
        if (numbers.length) stats.push({ href, value: Math.max(...numbers) });
      }
      if (stats.length >= 12) break;
    }
    return stats.filter(item => Number.isFinite(item.value));
  }

  function visibleYoutubeVideoStats() {
    const stats = [];
    const seen = new Set();
    const anchors = Array.from(document.querySelectorAll('a[href*="/watch"], a[href*="/shorts/"]'));
    const viewsPattern = /(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*(?:views|view|\u6b21\u89c2\u770b|\u6b21\u64ad\u653e)/i;

    for (const a of anchors) {
      const href = cleanUrl(new URL(a.getAttribute("href"), location.origin).href);
      if (!/(youtube\.com\/watch|youtube\.com\/shorts\/)/i.test(href) || seen.has(href)) continue;
      seen.add(href);

      let card = a.closest("ytd-rich-item-renderer, ytd-grid-video-renderer, ytd-video-renderer, ytd-reel-item-renderer");
      if (!card) {
        card = a;
        for (let i = 0; i < 7 && card && !viewsPattern.test(card.innerText || ""); i += 1) {
          card = card.parentElement;
        }
      }

      const text = [
        card?.innerText || "",
        a.getAttribute("aria-label") || "",
        a.getAttribute("title") || "",
        a.querySelector("img")?.getAttribute("alt") || ""
      ].join("\n");
      const match = text.match(viewsPattern);
      if (match) stats.push({ href, value: parseCompactNumber(match[1]) });
      if (stats.length >= 12) break;
    }

    if (!stats.length) {
      const text = pageText();
      for (const match of text.matchAll(viewsPattern)) {
        const value = parseCompactNumber(match[1]);
        if (Number.isFinite(value)) stats.push({ href: "", value });
        if (stats.length >= 12) break;
      }
    }

    return stats.filter(item => Number.isFinite(item.value));
  }

  function inferInstagramDisplayName(text, handle) {
    const rawHandle = String(handle || "").replace(/^@/, "");
    const lines = String(text || "")
      .split(/\n+/)
      .map(line => line.trim())
      .filter(Boolean)
      .filter(line => line.toLowerCase() !== rawHandle.toLowerCase())
      .filter(line => !line.includes("@"))
      .filter(line => !/^(posts|followers|following|message|follow|instagram|reels|tagged|posts)$/i.test(line))
      .filter(line => !/^(\d|[\d,.]+\s*(K|M|B|\u4e07|\u4ebf)?\s*(posts|followers|following|\u5e16\u5b50|\u7c89\u4e1d|\u5df2\u5173\u6ce8))/i.test(line));
    return lines[0] || rawHandle || handle || "";
  }

  function extractEmailFromPage(text) {
    const sources = [String(text || "")];
    for (const a of Array.from(document.querySelectorAll("a[href]"))) {
      const href = a.getAttribute("href") || "";
      const label = a.innerText || a.getAttribute("aria-label") || a.getAttribute("title") || "";
      if (/^mailto:/i.test(href)) sources.unshift(href.replace(/^mailto:/i, "").split("?")[0]);
      sources.push(href, label);
    }

    const directText = sources.join("\n");
    const direct = directText.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
    if (direct) return direct[0];

    const normalized = directText
      .replace(/\s*(?:\[|\(|\{)?\s*at\s*(?:\]|\)|\})?\s*/gi, "@")
      .replace(/\s*(?:\[|\(|\{)?\s*dot\s*(?:\]|\)|\})?\s*/gi, ".")
      .replace(/\s+@\s+/g, "@")
      .replace(/\s+\.\s+/g, ".");
    const obfuscated = normalized.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
    return obfuscated ? obfuscated[0] : "";
  }

  async function checkServer(server) {
    try {
      const res = await fetch(`${server}/health`, { cache: "no-store" });
      return res.ok;
    } catch {
      return false;
    }
  }

  function queryFromData(data) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(data)) {
      if (value !== undefined && value !== null && String(value).trim()) params.set(key, String(value));
    }
    return params.toString();
  }

  function scrapeVideoItem() {
    const text = pageText();
    const url = cleanUrl(location.href);
    const accountMatch =
      url.match(/tiktok\.com\/@([A-Za-z0-9._-]+)/i) ||
      url.match(/instagram\.com\/([A-Za-z0-9._-]+)\/(?:reel|p|tv)/i) ||
      text.match(/@([A-Za-z0-9._-]{2,})/);
    const likesMatch = text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*(?:likes|like|\u8d5e)/i);
    const viewsMatch = text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*(?:views|view|plays|play|\u64ad\u653e|\u89c2\u770b)/i);

    return {
      url,
      platform: platformFromUrl(url),
      title: document.title || "",
      account: accountMatch ? "@" + accountMatch[1].replace(/^@/, "") : handleFromUrl(url),
      likes: likesMatch ? formatNumber(parseCompactNumber(likesMatch[1])) : "",
      views: viewsMatch ? formatNumber(parseCompactNumber(viewsMatch[1])) : "",
      body_text: text.slice(0, 1200)
    };
  }

  function scrapeKolData() {
    const text = pageText();
    const profileText = profileTextOnly();
    const url = profileUrlForRecord(location.href);
    const platform = platformFromUrl(url);
    const handle = handleFromUrl(url);
    const visibleStats = platform === "Instagram"
      ? visibleInstagramPostStats()
      : platform === "YouTube"
        ? visibleYoutubeVideoStats()
        : [];
    const visibleValues = visibleStats.slice(0, 10).map(x => x.value);
    const email = extractEmailFromPage(profileText);
    const followersMatch =
      text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*Followers/i) ||
      text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*subscribers?/i) ||
      text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*(?:位)?\u8ba2\u9605\u8005/i) ||
      text.match(/Followers\s*(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)/i) ||
      text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*\u7c89\u4e1d/i) ||
      text.match(/\u7c89\u4e1d\s*(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)/i);
    const followers = followersMatch ? parseCompactNumber(followersMatch[1]) : null;

    let country = platform === "Instagram" ? "United States" : "";
    const profile = ` ${profileText} `;
    const countryAliases = [
      ["Germany", ["Germany", "\u5fb7\u56fd"]],
      ["Mexico", ["Mexico", "\u58a8\u897f\u54e5"]],
      ["United Kingdom", ["United Kingdom", " UK ", "\u82f1\u56fd"]],
      ["Australia", ["Australia", "\u6fb3\u5927\u5229\u4e9a"]],
      ["Canada", ["Canada", "\u52a0\u62ff\u5927"]],
      ["United States", ["United States", "USA", " U.S.", " US ", "\u7f8e\u56fd"]]
    ];
    for (const [standard, aliases] of countryAliases) {
      if (aliases.some(alias => profile.includes(alias))) {
        country = standard;
        break;
      }
    }

    const avg = avgNumber(visibleValues);
    const best = visibleValues.length ? Math.max(...visibleValues) : null;
    return {
      url,
      title: document.title || "",
      platform: kolPlatformFromUrl(url),
      handle,
      kol_name: platform === "Instagram" ? inferInstagramDisplayName(text, handle) : (platform === "YouTube" ? youtubeDisplayName(profileText, handle) : ""),
      email,
      country,
      followers: formatNumber(followers),
      avg_views: ["Instagram", "YouTube"].includes(platform) ? formatNumber(avg) : "",
      best_video_views: ["Instagram", "YouTube"].includes(platform) ? formatNumber(best) : "",
      notes: platform === "Instagram"
        ? (visibleValues.length
          ? `Instagram visible Reels views captured: ${visibleValues.length}; avg ${formatNumber(avg)}; best ${formatNumber(best)}.`
          : "Instagram profile did not show explicit views/plays; views left blank.")
        : ""
    };
  }

  function collectVisibleReels() {
    const seen = new Set();
    const items = [];
    for (const a of Array.from(document.querySelectorAll('a[href*="/reel/"]'))) {
      const href = cleanUrl(new URL(a.getAttribute("href"), location.origin).href);
      if (!/instagram\.com\/reel\//i.test(href) || seen.has(href)) continue;
      seen.add(href);
      let card = a.closest("article, div");
      for (let i = 0; i < 5 && card && (card.innerText || "").length < 20; i += 1) card = card.parentElement;
      const text = (card?.innerText || a.getAttribute("aria-label") || document.title || "").slice(0, 1000);
      const accountMatch = text.match(/@([A-Za-z0-9._-]{2,})/);
      const likesMatch = text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*(?:likes|like|\u8d5e)/i);
      const viewsMatch = text.match(/(\d+(?:[,.]\d+)*(?:\.\d+)?\s*[KMBkmb\u4e07\u4ebf]?)\s*(?:views|view|plays|play|\u64ad\u653e|\u89c2\u770b)/i);
      const gridNumbers = isInstagramProfileSubpage(location.href)
        ? extractNumbers(text).filter(n => Number.isFinite(n) && n >= 100)
        : [];
      const fallbackViews = gridNumbers.length ? Math.max(...gridNumbers) : null;
      items.push({
        url: href,
        platform: "Instagram",
        title: document.title || "Instagram Reel",
        account: accountMatch ? "@" + accountMatch[1].replace(/^@/, "") : handleFromUrl(location.href),
        likes: likesMatch ? formatNumber(parseCompactNumber(likesMatch[1])) : "",
        views: viewsMatch ? formatNumber(parseCompactNumber(viewsMatch[1])) : formatNumber(fallbackViews),
        body_text: text
      });
      if (items.length >= 30) break;
    }
    return items;
  }

  async function postVideoItems(items) {
    const res = await fetch(`${VIDEO_SERVER}/bulk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items })
    });
    return await res.json();
  }

  async function recordKol() {
    if (!(await checkServer(KOL_SERVER))) return setStatus(T.kolServerOff, false);
    if (!isKolProfileUrl(location.href)) return setStatus(T.kolNotPage, false);
    const data = scrapeKolData();
    const res = await fetch(`${KOL_SERVER}/add?${queryFromData(data)}`, { cache: "no-store" });
    const text = await res.text();
    if (!res.ok || !/recorded|已记录|KOL/i.test(text)) return setStatus("KOL record failed", false);
    const rowMatch = text.match(/第\s*(\d+)\s*行/);
    const parts = [
      data.handle || data.kol_name || "",
      rowMatch ? `row ${rowMatch[1]}` : "",
      data.followers ? `fans ${data.followers}` : "",
      data.avg_views ? `avg ${data.avg_views}` : ""
    ].filter(Boolean);
    setStatus(`KOL\u5df2\u8bb0\u5f55${parts.length ? ": " + parts.join(" / ") : ""}`);
  }

  async function collectCurrentVideo() {
    if (!(await checkServer(VIDEO_SERVER))) return setStatus(T.viralServerOff, false);
    if (!isVideoUrl(location.href)) return setStatus(T.videoNotPage, false);
    const data = await postVideoItems([scrapeVideoItem()]);
    setStatus(`Video saved ${data.saved || 0} / duplicate ${data.duplicates || 0} / failed ${data.failed || 0}`, data.failed === 0);
  }

  async function collectPageReels() {
    if (!(await checkServer(VIDEO_SERVER))) return setStatus(T.viralServerOff, false);
    if (!/instagram\.com/i.test(location.hostname)) return setStatus("Not an Instagram page", false);
    const items = collectVisibleReels();
    if (!items.length) return setStatus(T.reelsNotFound, false);
    const data = await postVideoItems(items);
    setStatus(`Reels saved ${data.saved || 0} / duplicate ${data.duplicates || 0} / failed ${data.failed || 0}`, data.failed === 0);
  }

  function setStatus(text, ok = true) {
    const el = document.getElementById("varla-unified-status");
    if (!el) return;
    el.textContent = text;
    el.style.color = ok ? "#0f7b3f" : "#b42318";
  }

  function button(text, handler, bg = "#245bdb") {
    const btn = document.createElement("button");
    btn.textContent = text;
    btn.style.cssText = `border:0;border-radius:6px;padding:8px 9px;background:${bg};color:white;font-weight:800;cursor:pointer;font-size:12px;`;
    btn.addEventListener("click", async () => {
      try {
        await handler();
      } catch (err) {
        setStatus(`Failed: ${err.message}`, false);
      }
    });
    return btn;
  }

  function clampPanelPosition(x, y, panel) {
    const margin = 8;
    const width = panel?.offsetWidth || 230;
    const height = panel?.offsetHeight || 290;
    return {
      x: Math.max(margin, Math.min(window.innerWidth - width - margin, Math.round(x))),
      y: Math.max(margin, Math.min(window.innerHeight - height - margin, Math.round(y)))
    };
  }

  function savePanelPosition(panel) {
    const pos = clampPanelPosition(panel.offsetLeft, panel.offsetTop, panel);
    try {
      if (chrome?.storage?.local) chrome.storage.local.set({ [PANEL_POS_KEY]: pos });
      else localStorage.setItem(PANEL_POS_KEY, JSON.stringify(pos));
    } catch {
      try { localStorage.setItem(PANEL_POS_KEY, JSON.stringify(pos)); } catch {}
    }
  }

  function loadPanelPosition(panel) {
    const apply = (pos) => {
      if (!pos || typeof pos.x !== "number" || typeof pos.y !== "number") return;
      const clamped = clampPanelPosition(pos.x, pos.y, panel);
      panel.style.left = `${clamped.x}px`;
      panel.style.top = `${clamped.y}px`;
      panel.style.right = "auto";
    };
    try {
      if (chrome?.storage?.local) {
        chrome.storage.local.get(PANEL_POS_KEY, data => apply(data?.[PANEL_POS_KEY]));
        return;
      }
    } catch {}
    try { apply(JSON.parse(localStorage.getItem(PANEL_POS_KEY) || "null")); } catch {}
  }

  function makeDraggable(panel, handle) {
    let dragging = false;
    let startX = 0;
    let startY = 0;
    let startLeft = 0;
    let startTop = 0;

    handle.addEventListener("pointerdown", event => {
      if (event.target?.dataset?.close) return;
      dragging = true;
      panel.setPointerCapture?.(event.pointerId);
      startX = event.clientX;
      startY = event.clientY;
      const rect = panel.getBoundingClientRect();
      startLeft = rect.left;
      startTop = rect.top;
      event.preventDefault();
    });

    window.addEventListener("pointermove", event => {
      if (!dragging) return;
      const pos = clampPanelPosition(startLeft + event.clientX - startX, startTop + event.clientY - startY, panel);
      panel.style.left = `${pos.x}px`;
      panel.style.top = `${pos.y}px`;
      panel.style.right = "auto";
    });

    window.addEventListener("pointerup", () => {
      if (!dragging) return;
      dragging = false;
      savePanelPosition(panel);
    });
  }

  async function refreshServerStatus() {
    const videoOk = await checkServer(VIDEO_SERVER);
    const kolOk = await checkServer(KOL_SERVER);
    const mode = isKolProfileUrl(location.href)
      ? "KOL\u4e3b\u9875"
      : isVideoUrl(location.href)
        ? "\u89c6\u9891\u9875"
        : /youtube\.com|youtu\.be/i.test(location.hostname)
          ? "YouTube\u9875\u9762"
        : /instagram\.com/i.test(location.hostname)
          ? "Instagram\u9875\u9762"
          : "\u666e\u901a\u9875\u9762";
    setStatus(`${mode} / \u7206\u6b3e${videoOk ? "\u5df2\u8fde" : "\u672a\u5f00"} / KOL${kolOk ? "\u5df2\u8fde" : "\u672a\u5f00"}`, videoOk || kolOk);
  }

  function injectPanel() {
    if (document.getElementById("varla-unified-panel")) return;
    const panel = document.createElement("div");
    panel.id = "varla-unified-panel";
    panel.style.cssText = [
      "position:fixed",
      "right:18px",
      "top:160px",
      "z-index:2147483647",
      "width:230px",
      "background:#fff",
      "border:1px solid #cfd7e6",
      "border-radius:8px",
      "box-shadow:0 10px 28px rgba(15,23,42,.14)",
      "font-family:Arial,'Microsoft YaHei',sans-serif",
      "padding:10px"
    ].join(";");

    const head = document.createElement("div");
    head.style.cssText = "display:flex;align-items:center;justify-content:space-between;gap:8px;cursor:move;margin-bottom:6px;";
    const title = document.createElement("strong");
    title.textContent = T.title;
    title.style.cssText = "font-size:15px;color:#111827;";
    const close = document.createElement("button");
    close.textContent = "\u00d7";
    close.dataset.close = "1";
    close.style.cssText = "border:0;background:transparent;font-size:18px;line-height:1;cursor:pointer;color:#667085;";
    close.addEventListener("click", () => panel.remove());
    head.append(title, close);

    const status = document.createElement("div");
    status.id = "varla-unified-status";
    status.style.cssText = "font-size:12px;line-height:1.35;margin:5px 0 8px;color:#475467;";
    status.textContent = "Checking...";

    const grid = document.createElement("div");
    grid.style.cssText = "display:grid;gap:7px;";
    grid.append(
      button(T.recordKol, recordKol),
      button(T.collectVideo, collectCurrentVideo),
      button(T.collectReels, collectPageReels),
      button(T.viralHub, () => window.open(`${VIDEO_SERVER}/`, "_blank"), "#344054"),
      button(T.kolLedger, () => window.open(`${KOL_SERVER}/`, "_blank"), "#344054")
    );

    panel.append(head, status, grid);
    document.documentElement.appendChild(panel);
    loadPanelPosition(panel);
    makeDraggable(panel, head);
    refreshServerStatus();
    setInterval(refreshServerStatus, 5000);
  }

  injectPanel();
})();

async function check(url) {
  try {
    const res = await fetch(url, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

function setStatus(id, ok, label) {
  const el = document.getElementById(id);
  el.className = "status " + (ok ? "ok" : "bad");
  el.textContent = `${label}: ${ok ? "connected" : "not running"}`;
}

async function refresh() {
  setStatus("video", await check("http://127.0.0.1:8766/health"), "Viral service 8766");
  setStatus("kol", await check("http://127.0.0.1:8765/health"), "KOL service 8765");
}

document.getElementById("openVideo").addEventListener("click", () => {
  chrome.tabs.create({ url: "http://127.0.0.1:8766" });
});

document.getElementById("openKol").addEventListener("click", () => {
  chrome.tabs.create({ url: "http://127.0.0.1:8765" });
});

refresh();

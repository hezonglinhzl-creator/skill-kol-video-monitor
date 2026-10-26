from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "varla_monitor.sqlite3"
DISCOVERY_INPUT = ROOT / "data" / "discovery_input.json"
UPDATE_INPUT = ROOT / "data" / "update_input.json"

CONTENT_MONITOR_FIELDS = [
    "Username",
    "Profile URL",
    "Post URL",
    "Shortcode",
    "Followers",
    "Views",
    "Likes",
    "Comments",
    "Classification",
    "Discovery Source",
    "First Seen",
    "Last Checked",
    "View Status",
]

KOL_RANKING_FIELDS = [
    "Username",
    "Profile URL",
    "Followers",
    "Varla Content Count",
    "Total Views",
    "Average Views",
    "Max Views",
    "Total Likes",
    "Total Comments",
    "Engagement Rate",
    "Views / Followers",
    "Last Checked",
]


@dataclass(frozen=True)
class ContentRecord:
    username: str
    profile_url: str
    post_url: str
    shortcode: str
    followers: int | None = None
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    classification: str = ""
    discovery_source: str = "instagram_public"
    view_status: str = "PENDING"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS instagram_contents (
            shortcode TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            profile_url TEXT NOT NULL,
            post_url TEXT NOT NULL,
            followers INTEGER,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            classification TEXT NOT NULL DEFAULT '',
            discovery_source TEXT NOT NULL DEFAULT 'instagram_public',
            first_seen_at TEXT NOT NULL,
            last_checked_at TEXT,
            view_status TEXT NOT NULL DEFAULT 'PENDING'
        );

        CREATE TABLE IF NOT EXISTS kol_rankings (
            username TEXT PRIMARY KEY,
            profile_url TEXT NOT NULL,
            followers INTEGER,
            varla_content_count INTEGER NOT NULL,
            total_views INTEGER NOT NULL,
            average_views REAL NOT NULL,
            max_views INTEGER NOT NULL,
            total_likes INTEGER NOT NULL,
            total_comments INTEGER NOT NULL,
            engagement_rate REAL NOT NULL,
            views_per_follower REAL NOT NULL,
            last_checked_at TEXT
        );
        """
    )
    conn.commit()


def load_json_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        return payload.get("records", [])
    if isinstance(payload, list):
        return payload
    raise ValueError(f"{path} must contain a JSON list or an object with records")


def int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(float(str(value).replace(",", "").strip()))


def normalize_record(raw: dict[str, Any]) -> ContentRecord:
    shortcode = str(raw.get("shortcode") or raw.get("Shortcode") or "").strip()
    if not shortcode:
        raise ValueError(f"missing shortcode: {raw}")
    username = str(raw.get("username") or raw.get("Username") or "").strip().lstrip("@")
    if not username:
        raise ValueError(f"missing username for {shortcode}")
    profile_url = str(raw.get("profile_url") or raw.get("Profile URL") or f"https://www.instagram.com/{username}/").strip()
    post_url = str(raw.get("post_url") or raw.get("Post URL") or f"https://www.instagram.com/reel/{shortcode}/").strip()
    return ContentRecord(
        username=username,
        profile_url=profile_url,
        post_url=post_url,
        shortcode=shortcode,
        followers=int_or_none(raw.get("followers") or raw.get("Followers")),
        views=int_or_none(raw.get("views") or raw.get("Views")),
        likes=int_or_none(raw.get("likes") or raw.get("Likes")),
        comments=int_or_none(raw.get("comments") or raw.get("Comments")),
        classification=str(raw.get("classification") or raw.get("Classification") or "").strip(),
        discovery_source=str(raw.get("discovery_source") or raw.get("Discovery Source") or "instagram_public").strip(),
        view_status=str(raw.get("view_status") or raw.get("View Status") or ("OK" if raw.get("views") else "PENDING")).strip(),
    )


def upsert_content(conn: sqlite3.Connection, record: ContentRecord, *, checked: bool) -> None:
    timestamp = now_iso()
    existing = conn.execute(
        "SELECT first_seen_at, views FROM instagram_contents WHERE shortcode = ?",
        (record.shortcode,),
    ).fetchone()
    first_seen = existing["first_seen_at"] if existing else timestamp
    last_checked = timestamp if checked else None
    if record.views is None and existing:
        views = existing["views"]
    else:
        views = record.views
    conn.execute(
        """
        INSERT INTO instagram_contents (
            shortcode, username, profile_url, post_url, followers, views, likes, comments,
            classification, discovery_source, first_seen_at, last_checked_at, view_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(shortcode) DO UPDATE SET
            username = excluded.username,
            profile_url = excluded.profile_url,
            post_url = excluded.post_url,
            followers = COALESCE(excluded.followers, instagram_contents.followers),
            views = ?,
            likes = COALESCE(excluded.likes, instagram_contents.likes),
            comments = COALESCE(excluded.comments, instagram_contents.comments),
            classification = excluded.classification,
            discovery_source = excluded.discovery_source,
            last_checked_at = COALESCE(excluded.last_checked_at, instagram_contents.last_checked_at),
            view_status = excluded.view_status
        """,
        (
            record.shortcode,
            record.username,
            record.profile_url,
            record.post_url,
            record.followers,
            views,
            record.likes,
            record.comments,
            record.classification,
            record.discovery_source,
            first_seen,
            last_checked,
            record.view_status,
            views,
        ),
    )


def aggregate(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM kol_rankings")
    conn.execute(
        """
        INSERT INTO kol_rankings (
            username, profile_url, followers, varla_content_count, total_views,
            average_views, max_views, total_likes, total_comments, engagement_rate,
            views_per_follower, last_checked_at
        )
        SELECT
            username,
            MAX(profile_url),
            MAX(followers),
            COUNT(*),
            COALESCE(SUM(views), 0),
            COALESCE(AVG(views), 0),
            COALESCE(MAX(views), 0),
            COALESCE(SUM(likes), 0),
            COALESCE(SUM(comments), 0),
            CASE WHEN COALESCE(SUM(views), 0) = 0 THEN 0
                 ELSE CAST(COALESCE(SUM(likes), 0) + COALESCE(SUM(comments), 0) AS REAL) / SUM(views)
            END,
            CASE WHEN MAX(followers) IS NULL OR MAX(followers) = 0 THEN 0
                 ELSE CAST(COALESCE(SUM(views), 0) AS REAL) / MAX(followers)
            END,
            MAX(last_checked_at)
        FROM instagram_contents
        GROUP BY username
        """
    )
    conn.commit()


def discover(conn: sqlite3.Connection) -> int:
    records = [normalize_record(item) for item in load_json_records(DISCOVERY_INPUT)]
    for record in records:
        upsert_content(conn, record, checked=False)
    conn.commit()
    return len(records)


def update(conn: sqlite3.Connection) -> int:
    records = [normalize_record(item) for item in load_json_records(UPDATE_INPUT)]
    for record in records:
        upsert_content(conn, record, checked=True)
    conn.commit()
    return len(records)


def rows_for_table(conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(f"SELECT * FROM {table}")]


def export_sync_json(conn: sqlite3.Connection) -> Path:
    out = ROOT / "data" / "feishu_sync_payload.json"
    payload = {
        "content_monitor_fields": CONTENT_MONITOR_FIELDS,
        "kol_ranking_fields": KOL_RANKING_FIELDS,
        "content_monitor": rows_for_table(conn, "instagram_contents"),
        "kol_ranking": rows_for_table(conn, "kol_rankings"),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def sync(conn: sqlite3.Connection) -> Path:
    payload = export_sync_json(conn)
    sync_script = ROOT / "sync_feishu.py"
    if sync_script.exists():
        subprocess.run(["python", str(sync_script), str(payload)], check=True)
    return payload


def run(command: str) -> None:
    with db() as conn:
        init_db(conn)
        if command == "discover":
            count = discover(conn)
            print(f"discovered_or_refreshed={count}")
        elif command == "update":
            count = update(conn)
            aggregate(conn)
            print(f"updated={count}")
        elif command == "sync":
            aggregate(conn)
            print(f"sync_payload={sync(conn)}")
        elif command == "all":
            discovered = discover(conn)
            updated = update(conn)
            aggregate(conn)
            payload = sync(conn)
            print(f"discovered_or_refreshed={discovered} updated={updated} sync_payload={payload}")


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Varla Instagram current-data monitor")
    parser.add_argument("command", choices=["discover", "update", "sync", "all"])
    args = parser.parse_args(argv)
    run(args.command)


if __name__ == "__main__":
    main()

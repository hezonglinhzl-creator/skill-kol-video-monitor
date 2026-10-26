from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "data" / "feishu_config.json"

CONTENT_MAP = {
    "username": "Username",
    "profile_url": "Profile URL",
    "post_url": "Post URL",
    "shortcode": "Shortcode",
    "followers": "Followers",
    "views": "Views",
    "likes": "Likes",
    "comments": "Comments",
    "classification": "Classification",
    "discovery_source": "Discovery Source",
    "first_seen_at": "First Seen",
    "last_checked_at": "Last Checked",
    "view_status": "View Status",
}

RANKING_MAP = {
    "username": "Username",
    "profile_url": "Profile URL",
    "followers": "Followers",
    "varla_content_count": "Varla Content Count",
    "total_views": "Total Views",
    "average_views": "Average Views",
    "max_views": "Max Views",
    "total_likes": "Total Likes",
    "total_comments": "Total Comments",
    "engagement_rate": "Engagement Rate",
    "views_per_follower": "Views / Followers",
    "last_checked_at": "Last Checked",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_lark(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(args, check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(result.stdout)


def field_payload(row: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    payload = {}
    for source, target in mapping.items():
        value = row.get(source)
        if value is None:
            continue
        payload[target] = value
    return payload


def existing_by_key(base_token: str, table_id: str, key_field: str, identity: str) -> dict[str, str]:
    response = run_lark(
        [
            "lark-cli",
            "base",
            "+record-list",
            "--base-token",
            base_token,
            "--table-id",
            table_id,
            "--field-id",
            key_field,
            "--limit",
            "200",
            "--as",
            identity,
            "--json",
        ]
    )
    data = response.get("data") or {}
    fields = data.get("fields") or []
    key_index = fields.index(key_field) if key_field in fields else -1
    records = {}
    for record_id, values in zip(data.get("record_id_list") or [], data.get("data") or []):
        if key_index >= 0 and key_index < len(values) and values[key_index]:
            records[str(values[key_index])] = record_id
    return records


def sync_rows(
    *,
    base_token: str,
    table_id: str,
    rows: list[dict[str, Any]],
    mapping: dict[str, str],
    key_field: str,
    source_key: str,
    identity: str,
) -> dict[str, int]:
    existing = existing_by_key(base_token, table_id, key_field, identity)
    creates = []
    updates = {}
    for row in rows:
        key = str(row.get(source_key) or "")
        if not key:
            continue
        payload = field_payload(row, mapping)
        record_id = existing.get(key)
        if record_id:
            updates[record_id] = payload
        else:
            creates.append(payload)

    if updates:
        tmp = ROOT / "data" / f"feishu_update_{table_id}.json"
        tmp.write_text(json.dumps({"update_records": updates}, ensure_ascii=False, indent=2), encoding="utf-8")
        run_lark(
            [
                "lark-cli",
                "base",
                "+record-batch-update",
                "--base-token",
                base_token,
                "--table-id",
                table_id,
                "--as",
                identity,
                "--json",
                f"@{tmp}",
            ]
        )
    if creates:
        tmp = ROOT / "data" / f"feishu_create_{table_id}.json"
        tmp.write_text(json.dumps({"create_records": creates}, ensure_ascii=False, indent=2), encoding="utf-8")
        run_lark(
            [
                "lark-cli",
                "base",
                "+record-batch-create",
                "--base-token",
                base_token,
                "--table-id",
                table_id,
                "--as",
                identity,
                "--json",
                f"@{tmp}",
            ]
        )
    return {"created": len(creates), "updated": len(updates)}


def main() -> None:
    payload_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "feishu_sync_payload.json"
    if not CONFIG_PATH.exists():
        print(f"feishu_config_missing={CONFIG_PATH}; exported_only={payload_path}")
        return

    config = load(CONFIG_PATH)
    payload = load(payload_path)
    base_token = config["base_token"]
    identity = config.get("identity", "user")
    content_result = sync_rows(
        base_token=base_token,
        table_id=config["content_monitor_table_id"],
        rows=payload.get("content_monitor") or [],
        mapping=CONTENT_MAP,
        key_field="Shortcode",
        source_key="shortcode",
        identity=identity,
    )
    ranking_result = sync_rows(
        base_token=base_token,
        table_id=config["kol_ranking_table_id"],
        rows=payload.get("kol_ranking") or [],
        mapping=RANKING_MAP,
        key_field="Username",
        source_key="username",
        identity=identity,
    )
    print(json.dumps({"content_monitor": content_result, "kol_ranking": ranking_result}, ensure_ascii=False))


if __name__ == "__main__":
    main()

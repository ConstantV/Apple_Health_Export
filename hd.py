#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import lzfse

APPLE_EPOCH_TO_UNIX = 978307200  # seconds between 1970-01-01 and 2001-01-01
LOCAL_TZ = ZoneInfo("Europe/Amsterdam")

STEP_METRICS = {
    "Step Count",
    "HKQuantityTypeIdentifierStepCount",
}


def apple_seconds_to_local_dt(value: float | int) -> datetime:
    """Apple epoch seconds -> timezone-aware datetime in Europe/Amsterdam."""
    unix_seconds = float(value) + APPLE_EPOCH_TO_UNIX
    dt_utc = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)
    return dt_utc.astimezone(LOCAL_TZ)


def apple_seconds_to_datetime_str(value: float | int) -> str:
    """Apple epoch seconds -> 'YYYY-MM-DD HH:MM:SS' in Europe/Amsterdam."""
    return apple_seconds_to_local_dt(value).strftime("%Y-%m-%d %H:%M:%S")


def apple_seconds_to_date_str(value: float | int) -> str:
    """Apple epoch seconds -> 'YYYY-MM-DD' in Europe/Amsterdam."""
    return apple_seconds_to_local_dt(value).strftime("%Y-%m-%d")


def convert_time_fields(obj):
    """
    Recursively walk JSON-like structure and replace numeric Apple epoch values for
    keys 'start', 'end', 'date', and 'time' with local datetime strings.
    """
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k in ("start", "end", "date", "time") and isinstance(v, (int, float)):
                obj[k] = apple_seconds_to_datetime_str(v)
            else:
                obj[k] = convert_time_fields(v)
        return obj

    if isinstance(obj, list):
        return [convert_time_fields(x) for x in obj]

    return obj  # primitives


def compute_total_steps(root: dict) -> int:
    """Sum all qty values in root['data'] and round to whole number."""
    rows = root.get("data", [])
    if not isinstance(rows, list):
        return 0

    total = 0.0
    for row in rows:
        if isinstance(row, dict):
            qty = row.get("qty")
            if isinstance(qty, (int, float)):
                total += float(qty)

    return int(round(total))


def simplify_step_json(root: dict) -> dict:
    """
    Return simplified JSON for Step Count:
    {
      "metric": "Step Count",
      "date": "YYYY-MM-DD",
      "Total_Steps": <int>
    }
    Date handling:
    - If root['date'] is a number (Apple epoch seconds), convert to YYYY-MM-DD.
    - If root['date'] is already a string, take first 10 chars as YYYY-MM-DD when possible.
    """
    metric = root.get("metric", "Step Count")
    total_steps = compute_total_steps(root)

    date_val = root.get("date")
    if isinstance(date_val, (int, float)):
        date_str = apple_seconds_to_date_str(date_val)
    elif isinstance(date_val, str):
        # Common cases: "2026-01-19 00:00:00" or "2026-01-19"
        date_str = date_val[:10] if len(date_val) >= 10 else date_val
    else:
        # Fallback: try to infer from first sample start, else blank
        rows = root.get("data", [])
        if isinstance(rows, list) and rows and isinstance(rows[0], dict) and isinstance(rows[0].get("start"), (int, float)):
            date_str = apple_seconds_to_date_str(rows[0]["start"])
        else:
            date_str = ""

    # Force exact key order you want
    return {
        "metric": metric if metric in STEP_METRICS else "Step Count",
        "date": date_str,
        "Total_Steps": total_steps,
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: hd.py <file.hae>")
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)

    raw = lzfse.decompress(p.read_bytes())
    data = json.loads(raw.decode("utf-8"))

    if isinstance(data, dict) and data.get("metric") in STEP_METRICS:
        # Step Count: keep only metric/date/Total_Steps
        simplified = simplify_step_json(data)
        out = p.with_suffix(".json")
        out.write_text(json.dumps(simplified, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {out} (simplified Step Count)")
        return

    # Non-step metrics: keep full JSON, but convert time fields for readability
    data = convert_time_fields(data)
    out = p.with_suffix(".json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

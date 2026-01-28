# Apple Health HAE Processor

This project provides tooling to **process Apple Health Auto Export (.hae) files locally** and convert them into **clean, privacy-friendly JSON** suitable for analysis, dashboards, and personal knowledge systems (such as TELOS / Obsidian).

The focus is on:
- transparency (no black boxes)
- local-first processing
- minimal data retention (only what is actually needed)
- incremental extensibility to additional health metrics

---

## What this project does

### Current functionality
- Decompresses **binary `.hae` files** (LZFSE compression)
- Parses the underlying Apple Health JSON data
- Converts Apple epoch timestamps to **local date/time (Europe/Amsterdam)**
- **Reduces Step Count data** to:
  - date (`YYYY-MM-DD`)
  - total number of steps (rounded)
- Writes a **cleaned JSON output** without raw samples

Example output (Step Count):

```json
{
  "metric": "Step Count",
  "date": "2026-01-19",
  "Total_Steps": 3715
}
```

---

## Why this approach?

Apple Health data is rich, but complex and often overkill for daily tracking.

This project therefore deliberately chooses:
- **daily aggregates instead of raw samples**
- **human-readable data**
- a clear separation between collection, normalization, and analysis

This fits well with:
- personal dashboards
- trend analysis
- journaling / sensemaking workflows (e.g. TELOS)

---

## What this project intentionally does NOT do

- No real-time synchronization
- No cloud uploads
- No automatic iCloud scraping
- No committing of privacy-sensitive raw data to Git

Everything runs **locally**, under explicit user control.

---

## Project structure

```text
health-export/
├── hd.py
├── requirements.txt
├── .gitignore
├── README.md
└── .venv/        (local only, not committed)
```

---

## Installation

### Requirements
- Python 3.10+
- macOS / Linux (Windows not tested)

### Virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### requirements.txt
```txt
lzfse
```

---

## Usage

```bash
python hd.py 20260126.hae
```

Result:
- `20260126.json` created in the same directory
- For Step Count: only date and total steps are retained

---

## Supported metrics (current)

| Metric      | Processing |
|------------|------------|
| Step Count | Daily total (sum, rounded) |

Other metrics are currently exported unmodified (with timestamp conversion) to allow investigation of their structure before defining aggregation rules.

---

## Privacy & Git

This project processes **personal health data**.

Therefore:
- `.hae` files are excluded via `.gitignore`
- generated `.json` files are also excluded
- only source code and configuration are committed

See `.gitignore` for details.

---

## Roadmap

Planned, incremental extensions:
- inventory of available Apple Health metrics
- configuration-driven aggregation rules per metric
- support for:
  - Active Energy
  - Heart Rate
  - HRV
  - Sleep Analysis
- optional exports to:
  - PostgreSQL
  - CSV
  - Markdown (TELOS / Obsidian daily logs)

---

## Philosophy

> Collect less. Understand more.

This project is not a data dump, but a **filter between Apple Health and insight**.

---

## Disclaimer

This is a personal / experimental project.  
Use at your own risk.

Apple Health and Health Auto Export are trademarks of their respective owners.

---

## Status

Actively developed.  
Current focus: explore → reduce → structure.

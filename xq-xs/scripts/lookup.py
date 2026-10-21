"""Search bundled XS identifiers and official example paths without network access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
HELP_KINDS = ("builtin", "system", "keyword", "quote", "data", "selection", "article")
PRESET_KINDS = ("function", "indicator", "sensor", "filter", "autotrade")


def search(records: list[dict], query: str, kind: str | None, limit: int) -> tuple[list[dict], int]:
    tokens = query.casefold().split()
    full = query.strip().casefold()
    matches = []
    for record in records:
        if kind and record["kind"] != kind:
            continue
        haystack = " ".join([record["name"], record["kind"], record.get("path", ""),
                             *record.get("categories", [])]).casefold()
        if not all(token in haystack for token in tokens):
            continue
        name = record["name"].casefold()
        score = 0 if name == full else 1 if name.startswith(full) else 2
        matches.append((score, record))
    matches.sort(key=lambda item: (item[0], item[1]["kind"], item[1].get("path", item[1]["name"]).casefold()))
    return [record for _, record in matches[:limit]], len(matches)


def load_index(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("records"), list):
        raise ValueError("Unsupported catalog schema")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Name, title, category, or space-separated path terms")
    parser.add_argument("--source", choices=("help", "preset", "all"), default="help")
    parser.add_argument("--kind", choices=HELP_KINDS + PRESET_KINDS)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if not args.query.strip() or not 1 <= args.limit <= 100:
        parser.error("Supply a non-empty query and --limit between 1 and 100")
    if ((args.source == "help" and args.kind in PRESET_KINDS)
            or (args.source == "preset" and args.kind in HELP_KINDS)):
        parser.error("--kind does not belong to the chosen --source")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sources = ("help", "preset") if args.source == "all" else (args.source,)
    records, provenance = [], {}
    try:
        for source in sources:
            data = load_index(DATA_DIR / f"{source}-index.json")
            records.extend(dict(row, source=source) for row in data["records"])
            provenance[source] = {key: data[key] for key in ("assembled_on", "scope", "commit") if key in data}
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Cannot read bundled catalog: {error}\n")
    results, total = search(records, args.query, args.kind, args.limit)
    if args.as_json:
        print(json.dumps({"query": args.query, "total": total, "returned": len(results),
                          "provenance": provenance, "results": results}, ensure_ascii=False, indent=2))
    else:
        print(f"{len(results)}/{total} matches. Index only; confirm current semantics in XSHelp.")
        for row in results:
            print(f"[{row['source']}:{row['kind']}] {row.get('path', row['name'])}")
            print(f"  {row['url']}")
            if row.get("link_type") == "search":
                print("  Search link: no direct help URL was present in the supplied snapshots.")
    return 0 if total else 1


if __name__ == "__main__":
    raise SystemExit(main())

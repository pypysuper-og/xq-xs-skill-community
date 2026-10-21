"""Build identifier-only indexes from supplied XS snapshots and a GitHub tree.

No manual prose or upstream script bodies are copied. This program is offline.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import parse_qs, quote, urlencode, urlsplit

TABLES = {
    "內建.md": "builtin",
    "系統.md": "system",
    "報價.md": "quote",
    "資料.md": "data",
    "選股.md": "selection",
    "關鍵字.md": "keyword",
    "XS語法運用.md": "article",
}
NAMESPACES = {
    "內建函數": "builtin", "系統函數": "system", "報價欄位": "quote",
    "資料欄位": "data", "選股欄位": "selection", "關鍵字": "keyword",
}
SCRIPT_KINDS = {
    "函數": "function", "指標": "indicator", "自動交易": "autotrade",
    "警示": "sensor", "選股": "filter",
}
ROW = re.compile(r"^\|\s*\d+-\d+\s*\|")
COMBINED = re.compile(r"^## ([^\n]+)\n\*\*Path:\*\* ([^\n]+)", re.MULTILINE)


def help_url(raw: str) -> str:
    """Canonicalize only identities actually present in a source URL."""
    parsed = urlsplit(raw)
    if (parsed.scheme != "https" or parsed.hostname != "xshelp.xq.com.tw"
            or parsed.netloc != parsed.hostname or not parsed.path.startswith("/XSHelp/")):
        raise ValueError("Expected an official XSHelp URL")
    query = parse_qs(parsed.query)
    if parsed.path.rstrip("/").endswith("/article"):
        if len(query.get("a", [])) != 1 or not query["a"][0]:
            raise ValueError("Help article must identify one topic")
        return "https://xshelp.xq.com.tw/XSHelp/article?" + urlencode(
            {"a": query["a"][0]}, quote_via=quote)
    if parsed.path.rstrip("/").endswith("/api"):
        name, group = query.get("a"), query.get("b")
    else:
        name, group = query.get("HelpName"), query.get("group")
    if not name or not group or len(name) != 1 or len(group) != 1:
        raise ValueError("Help URL must identify one name and group")
    return "https://xshelp.xq.com.tw/XSHelp/?" + urlencode(
        {"HelpName": name[0], "group": group[0].upper()}, quote_via=quote)


def table_rows(text: str, kind: str, source: str) -> tuple[list[dict], int]:
    records, skipped = [], 0
    for line in text.splitlines():
        if not ROW.match(line):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        needed = 5 if kind == "article" else 7
        if len(cells) < needed:
            raise ValueError(f"Malformed table row in {source}")
        if kind == "article":
            name, url, category = cells[3], cells[4], "語法運用"
            if not name:
                skipped += 1  # The supplied scrape includes a blank navigation row.
                continue
            parsed = urlsplit(url)
            if (parsed.scheme != "https" or parsed.netloc != "www.xq.com.tw"
                    or not parsed.path.startswith("/lesson/xspractice/")):
                raise ValueError(f"Unexpected article URL in {source}")
        else:
            category, name, raw = cells[3], cells[5], cells[6]
            if not name or not category:
                raise ValueError(f"Missing identifier/category in {source}")
            url = help_url(raw)
        records.append({"name": name, "kind": kind, "category": category,
                        "url": url, "source": source})
    return records, skipped


def combined_rows(text: str) -> list[dict]:
    records = []
    for name, path in COMBINED.findall(text):
        parts = [part.strip() for part in path.split(">")]
        if len(parts) != 2 or parts[0] not in NAMESPACES:
            raise ValueError(f"Unknown documentation namespace: {path}")
        records.append({"name": name.strip(), "kind": NAMESPACES[parts[0]],
                        "category": parts[1], "source": "all_documentation.md"})
    return records


def merge_records(rows: list[dict]) -> list[dict]:
    """Keep same-named quote/data/selection fields in separate namespaces."""
    merged: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = row["kind"], row["name"].casefold()
        record = merged.setdefault(key, {"name": row["name"], "kind": row["kind"],
                                         "categories": set(), "sources": set(), "urls": set()})
        record["categories"].add(row["category"])
        record["sources"].add(row["source"])
        if row.get("url"):
            record["urls"].add(row["url"])
    result = []
    for record in merged.values():
        urls = sorted(record.pop("urls"))
        record["link_type"] = "help" if urls else "search"
        if record["kind"] == "article":
            record["link_type"] = "article"
        record["url"] = urls[0] if urls else (
            "https://xshelp.xq.com.tw/XSHelp/search?" +
            urlencode({"a": record["name"]}, quote_via=quote))
        if len(urls) > 1:
            record["alternate_urls"] = urls[1:]
        record["categories"] = sorted(record["categories"])
        record["sources"] = sorted(record["sources"])
        result.append(record)
    return sorted(result, key=lambda row: (row["kind"], row["name"].casefold()))


def build_help(reference_dir: Path, assembled_on: str) -> dict:
    rows, inputs = [], []
    for name, kind in TABLES.items():
        path = reference_dir / name
        raw = path.read_bytes()
        imported, skipped = table_rows(raw.decode("utf-8-sig"), kind, name)
        if not imported:
            raise ValueError(f"No identifiers found in {name}")
        rows.extend(imported)
        inputs.append({"file": name, "sha256": hashlib.sha256(raw).hexdigest(),
                       "indexed_rows": len(imported), "skipped_navigation_rows": skipped})
    path = reference_dir / "all_documentation.md"
    raw = path.read_bytes()
    combined = combined_rows(raw.decode("utf-8-sig"))
    if not combined:
        raise ValueError("No entries found in all_documentation.md")
    rows.extend(combined)
    inputs.append({"file": path.name, "sha256": hashlib.sha256(raw).hexdigest(),
                   "indexed_rows": len(combined), "skipped_navigation_rows": 0})
    records = merge_records(rows)
    return {"schema_version": 1, "assembled_on": assembled_on,
            "scope": "Supplied snapshots; identifiers and links only; not a current API specification",
            "inputs": inputs, "counts": dict(sorted(Counter(r["kind"] for r in records).items())),
            "records": records}


def build_presets(tree: dict, commit: str, assembled_on: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("A full lowercase Git commit SHA is required")
    if tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
        raise ValueError("A complete, non-truncated GitHub recursive tree is required")
    tree_sha = tree.get("sha")
    if not isinstance(tree_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", tree_sha) or tree_sha == commit:
        raise ValueError("Fetch the tree using commit.tree.sha; a commit alias is not a tree object identity")
    records = []
    for entry in tree["tree"]:
        if entry.get("type") != "blob" or not entry.get("path", "").endswith(".xs"):
            continue
        path = entry["path"]
        parts = PurePosixPath(path).parts
        if (len(parts) < 2 or parts[0] not in SCRIPT_KINDS or ".." in parts
                or path.startswith("/") or "\\" in path or re.search(r"[\x00-\x1f]", path)):
            raise ValueError("Unexpected preset path")
        if not re.fullmatch(r"[0-9a-f]{40}", entry.get("sha", "")):
            raise ValueError("Missing preset blob identity")
        records.append({"name": PurePosixPath(path).stem, "kind": SCRIPT_KINDS[parts[0]],
                        "path": path, "blob_sha": entry["sha"],
                        "url": f"https://github.com/sysjust-xq/XScript_Preset/blob/{commit}/" +
                               quote(path, safe="/")})
    if not records:
        raise ValueError("No XS presets in tree")
    return {"schema_version": 1, "assembled_on": assembled_on,
            "repository": "sysjust-xq/XScript_Preset", "commit": commit,
            "tree_sha": tree_sha, "scope": "File identities only; no upstream script bodies",
            "counts": dict(sorted(Counter(r["kind"] for r in records).items())),
            "records": sorted(records, key=lambda row: row["path"])}


def write_index(path: Path, data: dict) -> None:
    """One record per line keeps generated indexes searchable and diffs bounded."""
    header = {key: value for key, value in data.items() if key != "records"}
    prefix = json.dumps(header, ensure_ascii=False, indent=2)[:-2]
    body = ",\n".join("    " + json.dumps(row, ensure_ascii=False, separators=(",", ":"))
                      for row in data["records"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prefix + ',\n  "records": [\n' + body + "\n  ]\n}\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--preset-tree", type=Path, required=True)
    parser.add_argument("--preset-commit", required=True)
    parser.add_argument("--assembled-on", type=date.fromisoformat, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "xq-xs" / "data")
    args = parser.parse_args()
    try:
        assembled = args.assembled_on.isoformat()
        help_index = build_help(args.reference_dir, assembled)
        preset_index = build_presets(json.loads(args.preset_tree.read_text(encoding="utf-8-sig")),
                                    args.preset_commit, assembled)
    except (OSError, UnicodeError, ValueError, KeyError) as error:
        parser.exit(2, f"Catalog build failed: {error}\n")
    write_index(args.output_dir / "help-index.json", help_index)
    write_index(args.output_dir / "preset-index.json", preset_index)
    print(json.dumps({"help": help_index["counts"], "presets": preset_index["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

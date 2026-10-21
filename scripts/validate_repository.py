"""Check skill structure, links, identifier provenance, and public text hygiene.

Offline packaging checks only. This does not parse, compile, or execute XS.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "xq-xs"
TEXT_SUFFIXES = {".md", ".yaml", ".json", ".py", ".xs"}
HELP_KINDS = {"builtin", "system", "keyword", "quote", "data", "selection", "article"}
PRESET_KINDS = {"function", "indicator", "sensor", "filter", "autotrade"}
PRIVATE_PATH = re.compile(r"[A-Za-z]:[\\/](?:Users|Warehouse)[\\/]", re.IGNORECASE)
MACHINE_HOME = re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/")
MARKDOWN_LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_url(url: str, host: str) -> None:
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and parsed.netloc == host,
            "Unexpected index URL origin")


def validate_indexes(skill: Path) -> tuple[int, int]:
    help_index = json.loads((skill / "data" / "help-index.json").read_text(encoding="utf-8"))
    preset_index = json.loads((skill / "data" / "preset-index.json").read_text(encoding="utf-8"))
    for data in (help_index, preset_index):
        require(data.get("schema_version") == 1, "Unsupported index schema")
        date.fromisoformat(data["assembled_on"])
        require(isinstance(data["records"], list) and bool(data["records"]), "Empty index")
        require(data["counts"] == dict(Counter(row["kind"] for row in data["records"])),
                "Index counts disagree with records")
    inputs = help_index["inputs"]
    source_names = {item["file"] for item in inputs}
    require(len(source_names) == len(inputs) == 8, "Expected eight distinct snapshot inputs")
    for item in inputs:
        require(item["file"] == Path(item["file"]).name, "Input identity must not be a machine path")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", item["sha256"])), "Invalid source hash")
        require(item["indexed_rows"] > 0 and item["skipped_navigation_rows"] >= 0, "Invalid input accounting")
    identities = set()
    allowed_help = {"name", "kind", "categories", "sources", "link_type", "url", "alternate_urls"}
    for row in help_index["records"]:
        require(set(row) <= allowed_help, "Help index contains content outside identifier metadata")
        require(row["kind"] in HELP_KINDS and bool(row["name"].strip()), "Invalid help identity")
        identity = row["kind"], row["name"].casefold()
        require(identity not in identities, "Duplicate help identity within namespace")
        identities.add(identity)
        require(bool(row["categories"]) and bool(row["sources"]), "Missing help provenance")
        require(set(row["sources"]) <= source_names, "Unknown snapshot source")
        require(row["link_type"] in {"help", "search", "article"}, "Unknown link type")
        require((row["kind"] == "article") == (row["link_type"] == "article"), "Article identity mismatch")
        for url in [row["url"], *row.get("alternate_urls", [])]:
            check_url(url, "www.xq.com.tw" if row["kind"] == "article" else "xshelp.xq.com.tw")
        if row["link_type"] == "search":
            require(urlsplit(row["url"]).path == "/XSHelp/search", "Search-only entry has an invented help URL")
    require(preset_index["repository"] == "sysjust-xq/XScript_Preset", "Unexpected preset repository")
    for key in ("commit", "tree_sha"):
        require(bool(re.fullmatch(r"[0-9a-f]{40}", preset_index[key])), "Invalid pinned upstream identity")
    require(preset_index["commit"] != preset_index["tree_sha"], "Commit alias mislabelled as tree object")
    paths = set()
    for row in preset_index["records"]:
        require(set(row) == {"name", "kind", "path", "blob_sha", "url"}, "Preset index contains script bodies")
        path = row["path"]
        require(row["kind"] in PRESET_KINDS and path not in paths, "Duplicate/unknown preset")
        require(".." not in PurePosixPath(path).parts and not path.startswith("/") and "\\" not in path,
                "Invalid preset path")
        require(path.endswith(".xs") and row["name"] == PurePosixPath(path).stem, "Preset filename mismatch")
        require(bool(re.fullmatch(r"[0-9a-f]{40}", row["blob_sha"])), "Invalid blob hash")
        expected = f"https://github.com/sysjust-xq/XScript_Preset/blob/{preset_index['commit']}/" + quote(path, safe="/")
        require(row["url"] == expected, "Preset URL is not pinned to its recorded commit/path")
        paths.add(path)
    return len(identities), len(paths)


def text_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*")
                  if path.is_file() and not set(path.relative_to(root).parts) &
                  {".git", "dist", "__pycache__", ".pytest_cache", ".codegraph"}
                  and (path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore", ".gitattributes"}))


def validate_tree(root: Path) -> tuple[int, int, int]:
    skill = root / "xq-xs"
    content = (skill / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
    require(frontmatter is not None, "Missing skill YAML frontmatter")
    require(re.search(r"^name: xq-xs$", frontmatter[1], re.MULTILINE) is not None, "Incorrect skill name")
    require(re.search(r"^description: .+", frontmatter[1], re.MULTILINE) is not None, "Missing skill description")
    ui = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    require('$xq-xs' in ui, "UI prompt must name the skill")
    require((root / "LICENSE").read_bytes() == (skill / "LICENSE").read_bytes(), "MIT license copies differ")
    files = text_files(root)
    for path in files:
        raw = path.read_bytes()
        require(not raw.startswith(b"\xef\xbb\xbf"), f"Unexpected UTF-8 BOM: {path.relative_to(root)}")
        text = raw.decode("utf-8")
        require(PRIVATE_PATH.search(text) is None and MACHINE_HOME.search(text) is None,
                f"Private machine path in {path.relative_to(root)}")
        if path.suffix == ".py":
            compile(text, str(path), "exec")
        if path.suffix == ".md":
            prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
            for target in MARKDOWN_LINK.findall(prose):
                target = target.strip("<>")
                if urlsplit(target).scheme or target.startswith("#"):
                    continue
                local = unquote(target.split("#", 1)[0])
                resolved = (path.parent / local).resolve()
                require(resolved.is_relative_to(root.resolve()) and resolved.exists(),
                        f"Broken local link in {path.relative_to(root)}: {local}")
                if path.is_relative_to(skill):
                    require(resolved.is_relative_to(skill.resolve()), "Skill link escapes installable folder")
    headers = {"indicator", "sensor", "filter", "autotrade", "function", "function_bool"}
    examples = list((skill / "assets" / "examples").glob("*.xs"))
    require(len(examples) == 6, "Expected six original XS examples")
    for path in examples:
        first = path.read_text(encoding="utf-8").splitlines()[0]
        require(any(first == f"{{@type:{kind}}}" for kind in headers), "Unexpected example type comment")
    help_count, preset_count = validate_indexes(skill)
    return len(files), help_count, preset_count


def main() -> int:
    try:
        files, help_count, preset_count = validate_tree(ROOT)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, SyntaxError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {files} UTF-8 source files; local links; public path hygiene; "
          f"{help_count} help/article identifiers; {preset_count} pinned presets.")
    print("XS example type comments checked; XS compilation/runtime not performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

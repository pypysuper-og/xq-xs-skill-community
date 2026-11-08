"""Check skill structure, links, identifier provenance, and public text hygiene.

Offline packaging checks only. This does not parse, compile, or execute XS.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
import json
import hashlib
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import parse_qs, quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "xq-xs"
TEXT_SUFFIXES = {".md", ".yaml", ".json", ".py", ".xs", ".toml", ".lock"}
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
                  {".git", "dist", "__pycache__", ".pytest_cache", ".codegraph", ".venv"}
                  and (path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore", ".gitattributes", ".python-version"}))


def validate_additions(skill: Path) -> None:
    articles = json.loads((skill / "data" / "articles-index.json").read_text(encoding="utf-8"))
    require(articles["schema_version"] == 1 and bool(articles["records"]), "Invalid article catalog")
    assembled = date.fromisoformat(articles["assembled_on"])
    check_url(articles["category_url"], "www.xq.com.tw")
    urls = set()
    for row in articles["records"]:
        require(set(row) == {"name", "kind", "published_on", "categories", "url"}, "Unexpected article body/metadata")
        require(row["kind"] == "article" and bool(row["name"]) and bool(row["categories"]), "Invalid article identity")
        require(date.fromisoformat(row["published_on"]) <= assembled, "Invalid article date")
        check_url(row["url"], "www.xq.com.tw")
        require(urlsplit(row["url"]).path.startswith("/xstrader/") and row["url"] not in urls, "Unexpected/duplicate article URL")
        urls.add(row["url"])
    require(set(articles.get("supplemental_urls", [])) <= urls,
            "Supplemental article URL has no catalog record")
    editor = skill / "assets" / "editor"
    source = json.loads((editor / "source.json").read_text(encoding="utf-8"))
    require(source["repository"] == "sysjust-xq/vscode-xs" and source["license"] == "MIT", "Unexpected editor source")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", source["commit"])), "Invalid editor commit")
    date.fromisoformat(source["reviewed_on"])
    for item in source["files"]:
        require(item["local"] == Path(item["local"]).name, "Editor asset must be a local filename")
        raw = (editor / item["local"]).read_bytes()
        variants = [raw, raw[:-1]] if raw.endswith(b"\n") else [raw]
        require(any(hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\0" + b).hexdigest() == item["blob_sha"]
                    for b in variants), "Bundled editor asset differs from its pinned upstream blob")
    grammar = json.loads((editor / "xs.tmLanguage.json").read_text(encoding="utf-8"))
    require(grammar["scopeName"] == "source.xs", "Unexpected editor grammar scope")
    require("Copyright (c) 2023 SysJust" in (skill / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8"),
            "Missing editor asset attribution")


def validate_supplement(skill: Path) -> int:
    data = json.loads((skill / "data" / "supplement-index.json").read_text(encoding="utf-8"))
    require(data["schema_version"] == 1 and bool(data["records"]) and bool(data["scope"]),
            "Invalid supplemental catalog")
    assembled = date.fromisoformat(data["assembled_on"])
    require(data["counts"] == dict(Counter(row["kind"] for row in data["records"])),
            "Supplement counts disagree with records")
    check_url(data["catalog_source"]["url"], "xshelp.xq.com.tw")
    require(re.fullmatch(r"[0-9a-f]{64}", data["catalog_source"]["sha256"]) is not None,
            "Invalid catalog source hash")
    groups = {"SDTFUNC": "builtin", "GENERALFUNC": "builtin", "FIELDFUNC": "builtin",
              "DECLARATION": "keyword", "STATSFUNC": "system", "PRICERELFUNC": "system",
              "FREQUENCYFUNC": "system"}
    identities = set()
    for row in data["records"]:
        require(set(row) == {"name", "kind", "categories", "url", "checked_on", "evidence"},
                "Supplement must contain identifier metadata only")
        identity = row["kind"], row["name"].casefold()
        require(bool(row["name"].strip()) and identity not in identities,
                "Invalid or duplicate supplemental identity")
        identities.add(identity)
        require(isinstance(row["categories"], list) and bool(row["categories"]),
                "Missing supplemental categories")
        require(date.fromisoformat(row["checked_on"]) <= assembled, "Invalid supplemental check date")
        require(row["evidence"] in {"help-page", "catalog-entry"}, "Unknown supplemental evidence")
        check_url(row["url"], "xshelp.xq.com.tw")
        url = urlsplit(row["url"])
        query = parse_qs(url.query)
        group = query.get("group", [None])[0]
        require(url.path == "/XSHelp/" and not url.fragment
                and set(query) == {"HelpName", "group"}
                and query["HelpName"] == [row["name"]] and len(query["group"]) == 1
                and group in groups and groups[group] == row["kind"],
                "Supplemental URL does not match its identifier namespace")
        require(row["evidence"] != "catalog-entry" or group == "SDTFUNC",
                "Catalog-only evidence is limited to the observed SDT catalog")
    manifest = json.loads((skill / "data" / "upstream-xscript.json").read_text(encoding="utf-8"))
    require(manifest["schema_version"] == 1 and manifest["upstream_code_executed"] is False,
            "Unexpected upstream review schema or execution claim")
    reviewed = date.fromisoformat(manifest["reviewed_on"])
    require(date.fromisoformat(manifest["article"]["published_on"]) <= reviewed,
            "Invalid upstream article date")
    check_url(manifest["article"]["url"], "www.xq.com.tw")
    archive = manifest["archive"]
    check_url(archive["url"], "drive.google.com")
    require(urlsplit(archive["url"]).query == "" and
            re.fullmatch(r"/file/d/[A-Za-z0-9_-]+/view", urlsplit(archive["url"]).path) is not None,
            "Archive source must be a public Drive page, not a download credential")
    require(archive["name"] == Path(archive["name"]).name and archive["name"].endswith(".zip")
            and re.fullmatch(r"[0-9a-f]{64}", archive["sha256"]) is not None,
            "Invalid upstream archive identity")
    require(bool(manifest["license_observation"]) and bool(manifest["integration"]),
            "Missing upstream rights or integration scope")
    members = manifest["members"]
    require(archive["bytes"] > 0 and len(members) == archive["file_count"] > 0
            and sum(row["bytes"] for row in members) == archive["uncompressed_bytes"],
            "Upstream member accounting disagrees with archive")
    paths = set()
    for row in members:
        require(set(row) == {"path", "bytes", "sha256"}, "Upstream manifest contains file bodies")
        path = row["path"]
        require(path.startswith("xscript/") and ".." not in PurePosixPath(path).parts
                and "\\" not in path and ":" not in path and path not in paths,
                "Invalid or duplicate upstream member path")
        require(row["bytes"] >= 0 and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None,
                "Invalid upstream member size or hash")
        paths.add(path)
    return len(identities)


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
    validate_additions(skill)
    validate_supplement(skill)
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
    print("Supplemental identifier provenance and upstream archive manifest checked offline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

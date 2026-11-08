"""Compile XS through an installed, logged-in XQ desktop. Not an XS compiler."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import uuid

TABLES = {"indicator": "Indicator", "filter": "Filter", "sensor": "Sensor", "autotrade": "AutoTrade"}
TYPE_HEADER = re.compile(r"\A\s*\{@type:([^}]+)\}[^\S\n]*(?:\n|$)")
EXIT_CODES = {"passed": 0, "ready": 0, "compile_error": 1, "environment_error": 2,
              "timeout": 3, "desktop_busy": 4}


def normalize_source(text: str, script_type: str) -> str:
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    header = TYPE_HEADER.match(text)
    if header:
        if header[1] != script_type:
            raise ValueError("The XS type comment disagrees with --type.")
        text = text[header.end():]
    if not text.strip() or "\x00" in text:
        raise ValueError("The source is empty or contains a NUL character.")
    return text.rstrip("\n") + "\n"


def stores(install_dir: Path) -> list[Path]:
    found = sorted((install_dir / "XS" / "Data" / "DAQXQLITE").glob("*/*_Script.sqlite"))
    if len(found) > 16:
        raise ValueError("Too many script stores; specify --script-store explicitly.")
    return found


def read_record(paths: list[Path], script_type: str, name: str) -> dict | None:
    """Read only the requested generated script, never enumerate users' scripts."""
    found = []
    for path in paths:
        if not path.is_file():
            raise ValueError("The requested XQ script store does not exist.")
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=1)) as db:
            db.execute("PRAGMA query_only=ON")
            db.row_factory = sqlite3.Row
            table = TABLES[script_type]  # Fixed allowlist, never user SQL.
            row = db.execute(
                f'SELECT ID,Name,CompileStatus,CompileMsg,LastCompileTime,LastCompileOKTime '
                f'FROM "{table}" WHERE Name=? COLLATE NOCASE', (name,)).fetchall()
            if len(row) > 1:
                raise ValueError("The generated script name is ambiguous in XQ.")
            if row:
                found.append({**dict(row[0]), "store": str(path.resolve())})
    if len(found) > 1:
        raise ValueError("The generated script exists in more than one account store.")
    return found[0] if found else None


def parse_record(row: dict) -> dict | None:
    """Status values are observed XQ desktop states; schema drift fails closed."""
    state = row["CompileStatus"]
    stamp = row["LastCompileTime"] or ""
    if state == 0 or not stamp or stamp.startswith("1970-01-01 "):
        return None
    if state not in (1, 2):
        raise ValueError(f"Unsupported XQ compilation status: {state!r}")
    if state == 1 and (not row["LastCompileOKTime"] or
                       row["LastCompileOKTime"] < row["LastCompileTime"]):
        return None
    raw = row["CompileMsg"] or ""
    messages = list(dict.fromkeys(line.strip() for line in raw.splitlines() if line.strip()))
    if state == 2 and not messages:
        raise ValueError("XQ reported a compilation error without a diagnostic message.")
    return {
        "status": "passed" if state == 1 else "compile_error",
        "diagnostics": [{"severity": "error" if state == 2 else "warning", "message": message,
                         "line": None, "column": None} for message in messages],
        "diagnostic_source": "xq-script-store-read-only",
        "locations_available": False,
        "raw_compiler_messages": raw,
        "last_compile_time": row["LastCompileTime"],
        "last_compile_ok_time": row["LastCompileOKTime"],
        "script_id": row["ID"],
        "message_count": len(messages),
        "diagnostic_detail_available": bool(messages) or state == 1,
    }


def parse_output(text: str, name: str) -> dict | None:
    """Require the exact generated name in XQ's terminal compiler output."""
    pattern = (r"^\[\d{2}:\d{2}:\d{2}\] " + re.escape(name) +
               r" 編譯(成功|發生錯誤)，(\d+)項錯誤，(\d+)項警告\s*$")
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    if not matches:
        return None
    match = matches[-1]
    errors, warnings = int(match[2]), int(match[3])
    if (match[1] == "成功") != (errors == 0):
        raise ValueError("The compiler summary contains contradictory status and error count.")
    return {"status": "passed" if errors == 0 else "compile_error",
            "error_count": errors, "warning_count": warnings,
            "compilation_output": text, "diagnostics": [], "locations_available": False,
            "diagnostic_detail_available": errors == warnings == 0,
            "diagnostic_source": "xq-editor-compilation-output"}


def combine_result(summary: dict, record: dict | None) -> dict:
    """A parser failure may appear only in the editor, leaving store status 7."""
    if record is None:
        return summary
    if summary["status"] != record["status"]:
        raise ValueError("The editor output and saved compilation status disagree.")
    return {**summary, **record, "compilation_output": summary["compilation_output"],
            "error_count": summary["error_count"], "warning_count": summary["warning_count"],
            "diagnostic_detail_available": bool(record["diagnostics"]) or
                summary["error_count"] == summary["warning_count"] == 0}


def run_backend(request: dict) -> dict:
    if os.name != "nt":
        raise ValueError("Compilation requires Windows with an interactive XQ desktop.")
    from xq_compile_windows import XqDesktop
    desktop = XqDesktop(request.get("xq_exe"))
    try:
        result = desktop.doctor() if request["operation"] == "Doctor" else desktop.compile(request)
    except TimeoutError as exc:
        result = {"status": "timeout", "reason": str(exc), "stage": desktop.stage,
                  "compile_trigger_attempted": desktop.trigger_attempted}
    except ValueError as exc:
        result = {"status": "environment_error", "reason": str(exc),
                  "stage": getattr(desktop, "stage", "preflight"),
                  "compile_trigger_attempted": getattr(desktop, "trigger_attempted", False)}
    if not isinstance(result, dict) or result.get("status") not in {
            "ready", "triggered", "environment_error", "desktop_busy", "timeout"}:
        raise ValueError("Unsupported desktop bridge response.")
    return result


def compile_source(args: argparse.Namespace) -> dict:
    deadline = time.monotonic() + args.timeout
    source = args.source.resolve()
    original = source.read_bytes()
    if len(original) > 512_000:
        raise ValueError("This desktop adapter accepts XS sources up to 512 KB.")
    decoded = original.decode("utf-8-sig").lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    header = TYPE_HEADER.match(decoded)
    text = normalize_source(decoded, args.type)
    doctor = run_backend({"operation": "Doctor", "xq_exe": args.xq_exe, "timeout": 20})
    if doctor["status"] != "ready":
        return doctor
    paths = [args.script_store.resolve()] if args.script_store else stores(Path(doctor["install_dir"]))
    if not paths:
        raise ValueError("No XQ personal-edition script store was found; log in to XQ first.")
    name = "XSC" + args.type[0] + uuid.uuid4().hex[:12]
    if read_record(paths, args.type, name) is not None:
        raise ValueError("Generated script name already exists; no existing script will be overwritten.")
    run_dir = args.work_dir.resolve() / name
    run_dir.mkdir(parents=True, exist_ok=False)
    submitted = run_dir / (name + ".xs")
    submitted.write_text(text, encoding="utf-8", newline="\r\n")
    request = {"operation": "Compile", "source": str(submitted), "source_text": text,
               "script_name": name, "script_type": args.type, "xq_exe": doctor["executable"],
               "timeout": max(1, deadline - time.monotonic()), "idle_seconds": args.idle_seconds,
               "evidence_dir": str(run_dir)}
    request_path = run_dir / "request.json"
    request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
    base = {"schema_version": 1, "backend": "xq-desktop", "script_type": args.type,
            "script_name": name, "source": str(source),
            "submitted_source": str(submitted),
            "source_line_offset": header[0].count("\n") if header else 0,
            "source_sha256": hashlib.sha256(original).hexdigest(),
            "normalized_source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "submitted_file_sha256": hashlib.sha256(submitted.read_bytes()).hexdigest(),
            "evidence_dir": str(run_dir), "xq_version": doctor.get("version"),
            "requires_xq": True, "requires_interactive_desktop": True,
            "captured_at": datetime.now(timezone.utc).isoformat()}
    bridge = {}
    try:
        bridge = run_backend(request)
        if bridge["status"] != "triggered":
            result = {**base, **bridge}
        else:
            if bridge.get("source_matches") is not True or bridge.get("type_matches") is not True:
                raise ValueError("Desktop bridge did not verify source and script type before compilation.")
            summary = parse_output(bridge.get("compilation_output", ""), name)
            row = read_record(paths, args.type, name)
            parsed = parse_record(row) if row else None
            if summary is not None:
                result = {**base, **combine_result(summary, parsed), "source_matches": True,
                          "type_matches": True, "compile_requested_at": bridge["compile_requested_at"]}
                for key in ("diagnostic_image", "diagnostic_capture_error"):
                    if key in bridge:
                        result[key] = bridge[key]
            else:
                result = {**base, "status": "timeout", "compile_trigger_attempted": True,
                          "reason": "No matching terminal compiler output before the deadline. Inspect XQ before retrying."}
    except (OSError, UnicodeError, ValueError, sqlite3.Error) as exc:
        result = {**base, "status": "environment_error", "reason": str(exc),
                  "compile_trigger_attempted": bridge.get("status") == "triggered"}
    result["captured_at"] = datetime.now(timezone.utc).isoformat()
    (run_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Read prerequisites without operating the editor.")
    doctor.add_argument("--xq-exe")
    doctor.add_argument("--json", action="store_true")
    compile_cmd = sub.add_parser("compile", help="Create an isolated script in XQ and compile only.")
    compile_cmd.add_argument("source", type=Path)
    compile_cmd.add_argument("--type", choices=TABLES, required=True)
    compile_cmd.add_argument("--xq-exe")
    compile_cmd.add_argument("--script-store", type=Path)
    compile_cmd.add_argument("--work-dir", type=Path, required=True)
    compile_cmd.add_argument("--timeout", type=int, default=120)
    compile_cmd.add_argument("--idle-seconds", type=int, default=10)
    compile_cmd.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            result = run_backend({"operation": "Doctor", "xq_exe": args.xq_exe, "timeout": 20})
        else:
            if not 10 <= args.timeout <= 300 or not 0 <= args.idle_seconds <= 60:
                raise ValueError("Timeout must be 10–300 seconds; idle wait must be 0–60 seconds.")
            if os.name != "nt":
                raise ValueError("Compilation requires Windows with an interactive XQ desktop.")
            from xq_compile_windows import desktop_lock
            with desktop_lock() as acquired:
                result = compile_source(args) if acquired else {
                    "status": "desktop_busy", "reason": "Another desktop compiler owns this session."}
    except (OSError, UnicodeError, ValueError, sqlite3.Error) as exc:
        result = {"status": "environment_error", "reason": str(exc)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(result["status"])
        if result.get("reason"):
            print(result["reason"])
        for item in result.get("diagnostics", []):
            print(item["severity"] + ": " + item["message"])
    return EXIT_CODES[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())

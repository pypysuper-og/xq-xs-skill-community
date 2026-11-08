from __future__ import annotations

import importlib.util
import argparse
import json
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "xq-xs" / "scripts" / "xq_compile.py"
spec = importlib.util.spec_from_file_location("xs_compiler", SCRIPT)
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)


class SourceTests(unittest.TestCase):
    def test_header_kind_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            compiler.normalize_source("{@type:autotrade}\nSetPosition(0);", "indicator")

    def test_type_comment_and_utf8_bom_are_not_submitted_as_code(self):
        self.assertEqual(compiler.normalize_source('\ufeff{@type:indicator}\r\n// 中文\r\nPlot1(Close);\r\n', "indicator"),
                         "// 中文\nPlot1(Close);\n")

    def test_empty_and_nul_are_rejected_before_desktop_input(self):
        for text in ("", " \n", "Plot1(Close);\x00"):
            with self.assertRaises(ValueError):
                compiler.normalize_source(text, "indicator")


class DiagnosticTests(unittest.TestCase):
    @staticmethod
    def row(**overrides):
        return {"ID": "owned", "CompileStatus": 1, "CompileMsg": "",
                "LastCompileTime": "2026-11-08 10:00:00", "LastCompileOKTime": "2026-11-08 10:00:01", **overrides}

    def test_success_requires_completed_success_time(self):
        self.assertEqual(compiler.parse_record(self.row())["status"], "passed")
        self.assertIsNone(compiler.parse_record(self.row(LastCompileOKTime="1970-01-01 08:00:00")))

    def test_error_messages_preserve_unicode_and_do_not_invent_positions(self):
        result = compiler.parse_record(self.row(CompileStatus=2, CompileMsg="未知的關鍵字 ProbeTypo\r\n未知的關鍵字 ProbeTypo\r\n缺少右括號"))
        self.assertEqual(result["status"], "compile_error")
        self.assertEqual(result["message_count"], 2)
        self.assertEqual(result["diagnostics"][0]["message"], "未知的關鍵字 ProbeTypo")
        self.assertIsNone(result["diagnostics"][0]["line"])
        self.assertFalse(result["locations_available"])

    def test_pending_unknown_and_empty_failure_are_not_passes(self):
        self.assertIsNone(compiler.parse_record(self.row(CompileStatus=0)))
        self.assertIsNone(compiler.parse_record(self.row(LastCompileTime="1970-01-01 08:00:00")))
        self.assertIsNone(compiler.parse_record(self.row(CompileStatus=7, LastCompileTime="1970-01-01 08:00:00.000")))
        for state, message in ((3, "unsupported"), (2, "")):
            with self.assertRaises(ValueError):
                compiler.parse_record(self.row(CompileStatus=state, CompileMsg=message))

    def test_editor_failure_is_returned_when_store_remains_uncompiled(self):
        output = "[00:10:00] XSCfilter 編譯開始\r\n[00:10:01] XSCfilter 編譯發生錯誤，1項錯誤，0項警告"
        summary = compiler.parse_output(output, "XSCfilter")
        pending = compiler.parse_record(self.row(CompileStatus=7, LastCompileTime="1970-01-01 08:00:00.000"))
        result = compiler.combine_result(summary, pending)
        self.assertEqual(result["status"], "compile_error")
        self.assertEqual(result["error_count"], 1)
        self.assertFalse(result["diagnostic_detail_available"])
        self.assertEqual(result["diagnostics"], [])

    def test_other_script_summary_cannot_complete_this_request(self):
        output = "[00:10:01] OtherScript 編譯成功，0項錯誤，0項警告"
        self.assertIsNone(compiler.parse_output(output, "ThisScript"))

    def test_editor_summary_and_store_disagreement_is_not_a_pass(self):
        summary = compiler.parse_output("[00:10:01] Owned 編譯發生錯誤，1項錯誤，0項警告", "Owned")
        with self.assertRaises(ValueError):
            compiler.combine_result(summary, compiler.parse_record(self.row()))

    def test_summary_status_and_error_count_must_agree(self):
        with self.assertRaises(ValueError):
            compiler.parse_output("[00:10:01] Owned 編譯成功，1項錯誤，0項警告", "Owned")


class StoreTests(unittest.TestCase):
    @staticmethod
    def make_store(path, name="OwnedProbe"):
        with closing(sqlite3.connect(path)) as db:
            with db:
                db.execute("CREATE TABLE Indicator (ID,Name,CompileStatus,CompileMsg,LastCompileTime,LastCompileOKTime)")
                db.execute("INSERT INTO Indicator VALUES (?,?,?,?,?,?)",
                           ("id", name, 1, "", "2026-11-08 10:00:00", "2026-11-08 10:00:01"))

    def test_only_requested_name_is_returned_and_read_is_nonmutating(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "script.sqlite"
            self.make_store(path)
            before = path.read_bytes()
            self.assertIsNone(compiler.read_record([path], "indicator", "OtherScript"))
            self.assertEqual(compiler.read_record([path], "indicator", "ownedprobe")["ID"], "id")
            self.assertEqual(path.read_bytes(), before)

    def test_missing_database_is_not_created(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "missing.sqlite"
            with self.assertRaises(ValueError):
                compiler.read_record([path], "indicator", "OwnedProbe")
            self.assertFalse(path.exists())

    def test_duplicate_name_across_accounts_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp) / name for name in ("one.sqlite", "two.sqlite")]
            for path in paths:
                self.make_store(path)
            with self.assertRaises(ValueError):
                compiler.read_record(paths, "indicator", "OwnedProbe")


class WorkflowTests(unittest.TestCase):
    def test_pending_store_failure_and_schema_error_keep_evidence_after_trigger(self):
        for state, expected in ((7, "compile_error"), (3, "environment_error")):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                source = folder / "source.xs"
                source.write_text("{@type:filter}\nRet = UnknownIdentifier;\n", encoding="utf-8")
                args = argparse.Namespace(source=source, type="filter", timeout=30, xq_exe=None,
                                          script_store=None, work_dir=folder / "evidence", idle_seconds=10)
                def backend(request):
                    if request["operation"] == "Doctor":
                        return {"status": "ready", "install_dir": str(folder), "executable": "xq.exe", "version": "test"}
                    return {"status": "triggered", "source_matches": True, "type_matches": True,
                            "compile_requested_at": "test", "diagnostic_image": "test-image.bmp",
                            "compilation_output": f'[00:10:00] {request["script_name"]} 編譯發生錯誤，1項錯誤，0項警告'}
                row = DiagnosticTests.row(CompileStatus=state, CompileMsg="",
                                          LastCompileTime="1970-01-01 08:00:00.000" if state == 7 else "2026-11-08 10:00:00")
                with patch.object(compiler, "run_backend", side_effect=backend), \
                        patch.object(compiler, "stores", return_value=[folder / "store.sqlite"]), \
                        patch.object(compiler, "read_record", side_effect=[None, row]):
                    result = compiler.compile_source(args)
                saved = json.loads((Path(result["evidence_dir"]) / "result.json").read_text(encoding="utf-8"))
                self.assertEqual(saved["status"], expected)
                self.assertEqual(saved["source_line_offset"], 1)
                self.assertTrue(Path(saved["submitted_source"]).is_file())
                if state == 7:
                    self.assertFalse(saved["diagnostic_detail_available"])
                    self.assertEqual(saved["diagnostic_image"], "test-image.bmp")
                else:
                    self.assertTrue(saved["compile_trigger_attempted"])


if __name__ == "__main__":
    unittest.main()

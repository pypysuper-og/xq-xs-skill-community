from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_catalogs as catalogs
import build_package as packaging
import validate_repository as validation

spec = importlib.util.spec_from_file_location("xs_lookup", ROOT / "xq-xs" / "scripts" / "lookup.py")
lookup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lookup)


class CatalogTests(unittest.TestCase):
    def test_multiline_scrape_ignores_body_and_keeps_identity(self):
        text = ('| 1748876225-1 | start | 欄位函數 | category | GetField | '
                'https://xshelp.xq.com.tw/XSHelp/?HelpName=GetField&group=FIELDFUNC | body\n'
                'source prose | more prose\n'
                '| 1748876226-2 | start | 欄位函數 | category | GetQuote | '
                'https://xshelp.xq.com.tw/XSHelp/?HelpName=GetQuote&group=FIELDFUNC | body')
        rows, skipped = catalogs.table_rows(text, "builtin", "fixture.md")
        self.assertEqual([row["name"] for row in rows], ["GetField", "GetQuote"])
        self.assertEqual(skipped, 0)
        self.assertNotIn("body", json.dumps(rows))

    def test_keyword_api_url_preserves_identity(self):
        self.assertEqual(catalogs.help_url("https://xshelp.xq.com.tw/XSHelp/api?a=Input&b=declaration"),
                         "https://xshelp.xq.com.tw/XSHelp/?HelpName=Input&group=DECLARATION")

    def test_keyword_article_does_not_require_invented_group(self):
        url = "https://xshelp.xq.com.tw/XSHelp/article?a=Begin_End"
        self.assertEqual(catalogs.help_url(url), url)

    def test_foreign_help_url_rejected(self):
        with self.assertRaises(ValueError):
            catalogs.help_url("https://example.com/XSHelp/?HelpName=GetField&group=FIELDFUNC")

    def test_navigation_row_excluded_but_counted(self):
        rows, skipped = catalogs.table_rows('| 123-1 | start |  | https://www.xq.com.tw/lesson/xspractice | body |',
                                             "article", "fixture.md")
        self.assertEqual((rows, skipped), ([], 1))

    def test_combined_file_includes_final_entry(self):
        text = '## 收盤價\n**Path:** 資料欄位 > 價格\nprose\n## 收盤價\n**Path:** 選股欄位 > 價格'
        self.assertEqual([row["kind"] for row in catalogs.combined_rows(text)], ["data", "selection"])

    def test_unknown_namespace_is_visible_error(self):
        with self.assertRaises(ValueError):
            catalogs.combined_rows("## Sample\n**Path:** 新分類 > 未知")

    def test_same_name_keeps_namespaces_and_merges_duplicate_categories(self):
        rows = [{"name": "收盤價", "kind": kind, "category": cat, "source": source,
                 "url": f"https://xshelp.xq.com.tw/XSHelp/?HelpName=Close&group={kind}"}
                for kind, cat, source in [("data", "價格", "one"), ("data", "常用", "two"),
                                          ("quote", "價格", "one"), ("selection", "價格", "one")]]
        result = catalogs.merge_records(rows)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["categories"], ["價格", "常用"])
        self.assertEqual(result[0]["sources"], ["one", "two"])

    def test_missing_direct_link_is_search_not_invented_help(self):
        result = catalogs.merge_records([{"name": "新欄位", "kind": "data", "category": "價格", "source": "one"}])[0]
        self.assertEqual(result["link_type"], "search")
        self.assertEqual(urlsplit(result["url"]).path, "/XSHelp/search")
        self.assertNotIn("group", result["url"])

    def test_preset_paths_are_percent_encoded_and_pinned(self):
        tree = {"sha": "b" * 40, "truncated": False, "tree": [
            {"type": "blob", "path": "自動交易/範例#1.xs", "sha": "c" * 40}]}
        row = catalogs.build_presets(tree, "a" * 40, "2026-10-21")["records"][0]
        self.assertEqual(urlsplit(row["url"]).fragment, "")
        self.assertIn("%231", row["url"])
        self.assertIn("自動交易/範例#1.xs", unquote(row["url"]))
        self.assertEqual(row["kind"], "autotrade")

    def test_truncated_tree_rejected(self):
        with self.assertRaises(ValueError):
            catalogs.build_presets({"truncated": True, "tree": []}, "a" * 40, "2026-10-21")

    def test_commit_alias_cannot_be_recorded_as_tree_object(self):
        tree = {"sha": "a" * 40, "truncated": False, "tree": [
            {"type": "blob", "path": "指標/Sample.xs", "sha": "c" * 40}]}
        with self.assertRaises(ValueError):
            catalogs.build_presets(tree, "a" * 40, "2026-10-21")

    def test_preset_path_traversal_rejected(self):
        tree = {"sha": "b" * 40, "truncated": False,
                "tree": [{"type": "blob", "path": "指標/../bad.xs", "sha": "c" * 40}]}
        with self.assertRaises(ValueError):
            catalogs.build_presets(tree, "a" * 40, "2026-10-21")

    def test_generated_json_round_trips_unicode(self):
        data = {"schema_version": 1, "records": [{"name": "收盤價", "kind": "data"}]}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "index.json"
            catalogs.write_index(path, data)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), data)
            self.assertNotIn(b"\r\n", path.read_bytes())


class LookupTests(unittest.TestCase):
    def test_exact_name_first_case_insensitive_and_bounded(self):
        rows = [{"name": "GetFieldDate", "kind": "builtin"}, {"name": "GetField", "kind": "builtin"}]
        found, total = lookup.search(rows, "getfield", None, 1)
        self.assertEqual((found[0]["name"], total), ("GetField", 2))

    def test_multiple_terms_intersect_and_kind_filters(self):
        rows = [{"name": "Fill", "kind": "autotrade", "path": "自動交易/Position跟Filled.xs"},
                {"name": "Position", "kind": "function", "path": "函數/Position.xs"}]
        found, total = lookup.search(rows, "Position Filled", "autotrade", 8)
        self.assertEqual((len(found), total), (1, 1))

    def test_cli_works_outside_checkout_and_outputs_utf8_json(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT / "xq-xs" / "scripts" / "lookup.py"),
                                     "收盤價", "--kind", "selection", "--json"], cwd=temp,
                                    capture_output=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["results"][0]["kind"], "selection")
        self.assertEqual(data["results"][0]["name"], "收盤價")

    def test_missing_query_is_not_a_false_success(self):
        result = subprocess.run([sys.executable, str(ROOT / "xq-xs" / "scripts" / "lookup.py"),
                                 "not-a-real-xs-identifier", "--json"], capture_output=True,
                                encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["total"], 0)

    def test_mismatched_source_kind_rejected(self):
        result = subprocess.run([sys.executable, str(ROOT / "xq-xs" / "scripts" / "lookup.py"),
                                 "Close", "--source", "preset", "--kind", "data"],
                                capture_output=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 2)


class DistributionTests(unittest.TestCase):
    def test_committed_indexes_have_no_body_and_preserve_provenance(self):
        help_count, preset_count = validation.validate_indexes(ROOT / "xq-xs")
        self.assertGreater(help_count, 1000)
        self.assertGreater(preset_count, 1000)

    def test_archive_is_self_contained_and_lookup_runs_after_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "skill.zip"
            digest, count = packaging.build_package(ROOT / "xq-xs", output)
            with ZipFile(output) as archive:
                names = archive.namelist()
                self.assertEqual(count, len(names))
                self.assertIn("xq-xs/SKILL.md", names)
                self.assertIn("xq-xs/LICENSE", names)
                self.assertTrue(all(name.startswith("xq-xs/") for name in names))
                self.assertFalse(any("__pycache__" in name or name.startswith("tests/") for name in names))
                archive.extractall(folder / "installed")
            self.assertIn(digest, output.with_suffix(".zip.sha256").read_text(encoding="utf-8"))
            result = subprocess.run([sys.executable, str(folder / "installed" / "xq-xs" / "scripts" / "lookup.py"),
                                     "Position Filled", "--source", "preset", "--json"], cwd=folder,
                                    capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["results"][0]["kind"], "autotrade")

    def test_archive_cannot_overwrite_its_source_tree(self):
        with self.assertRaises(ValueError):
            packaging.build_package(ROOT / "xq-xs", ROOT / "xq-xs" / "archive.zip")


if __name__ == "__main__":
    unittest.main()

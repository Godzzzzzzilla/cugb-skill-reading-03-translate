#!/usr/bin/env python3
"""Self-test for reading-03-translate."""
from __future__ import annotations
import json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import armkit as ak
import run as skill
PASS = FAIL = 0
def check(n, c, d=""):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ok {n}" + (f" — {d}" if d else ""))
    else: FAIL += 1; print(f"  FAIL {n}" + (f" — {d}" if d else ""))
def main():
    print("reading-03 selftest")
    check("armkit pinned", bool(ak.VERSION), ak.VERSION)
    segs = skill.segment("# Title\n\nFirst sentence here. Second sentence follows.")
    check("segments include heading", segs[0]["kind"] == "heading", segs[0]["text"])
    check("segments split sentences", len([s for s in segs if s["kind"] == "sentence"]) == 2)
    check("term matching ignores hyphens", skill.has_term("reading-order recovery", "reading order"))
    with tempfile.TemporaryDirectory() as td:
        case = ak.CaseInput.load(os.path.join(ROOT, "examples", "case.json"))
        audit, res = ak.Audit("t"), ak.Result(td, "reading-03")
        ok = skill.solve(case, td, audit, res)
        doc = res.write(case, audit, ak.derive_status(audit, ok), "t", ak.utc_now(), ["selftest"])
        check("demo completes", ok)
        check("status success", doc["status"] == "success", doc["status"])
        check("glossary fully consistent", doc["result"]["consistency"]["consistent"] == doc["result"]["consistency"]["terms"])
        check("translation written", os.path.isfile(os.path.join(td, "translation.md")))
        bad = [e for e in doc["evidence"] if not ak.verify_anchor(td, e["anchor"])[0]]
        check("anchors re-slice", not bad, f"{len(doc['evidence'])} anchors")
    # a translation that drops a sentence and changes a number must be rejected by the audit
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "in"))
        open(os.path.join(td, "in", "src.md"), "w", encoding="utf-8").write(
            "We measure 71.4% recall on three pages. The gutter is 20 pt wide. Results are stable.")
        open(os.path.join(td, "in", "translation_zh.md"), "w", encoding="utf-8").write(
            "我们测量了三页上的 71.4% 召回率。栏间距为 20 pt。")
        json.dump({"id": "bad"}, open(os.path.join(td, "in", "case.json"), "w", encoding="utf-8"))
        case = ak.CaseInput.load(os.path.join(td, "in", "case.json"))
        audit, res = ak.Audit("t2"), ak.Result(os.path.join(td, "o"), "reading-03")
        skill.solve(case, os.path.join(td, "o"), audit, res)
        checks = {c["id"]: c["ok"] for c in audit.checks}
        check("dropped sentence detected", not checks.get("all-segments-translated", True),
              str(res.payload.get("segment_count")))
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "in"))
        open(os.path.join(td, "in", "src.md"), "w", encoding="utf-8").write("We report 71.4% and 20 pt.")
        open(os.path.join(td, "in", "translation_zh.md"), "w", encoding="utf-8").write("我们报告 71.4% 与 20 pt。")
        json.dump({"id": "n"}, open(os.path.join(td, "in", "case.json"), "w", encoding="utf-8"))
        case = ak.CaseInput.load(os.path.join(td, "in", "case.json"))
        audit, res = ak.Audit("t3"), ak.Result(os.path.join(td, "o3"), "reading-03")
        skill.solve(case, os.path.join(td, "o3"), audit, res)
        checks = {c["id"]: c["ok"] for c in audit.checks}
        check("complete translation passes", checks.get("numbers-preserved") and checks.get("units-preserved"))
    print(f"\n{PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1
if __name__ == "__main__":
    raise SystemExit(main())

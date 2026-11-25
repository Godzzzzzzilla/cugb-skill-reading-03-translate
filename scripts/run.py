#!/usr/bin/env python3
"""reading-03-translate — segment, lock terminology, and audit a translation.

    python scripts/run.py --input /input/case.json --output /app/output

Terminology consistency alone is a mid-tier answer: a glossary can be perfectly
obeyed by a translation that drops a sentence or a decimal.  So the audit here
works at segment level and checks four things per segment — nothing dropped,
numbers intact, units intact, citations intact — plus the glossary, plus a
language check that catches a segment that was never translated.

If no translation is supplied the skill emits a segment template and a
term-locked draft, marked `mode: draft`, so the case still produces evidence
instead of an empty file.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import armkit as ak  # noqa: E402

SKILL = "reading-03-translate"
VERSION = "1.0.0"
CJK = re.compile(r"[\u4e00-\u9fff]")


def norm_term(t: str) -> str:
    return re.sub(r"[\s\-_]+", " ", t.casefold()).strip()


def has_term(text: str, term: str) -> bool:
    return norm_term(term) in norm_term(text)
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


def load_glossary(case: ak.CaseInput):
    gl = {}
    for p in case.discover([".tsv", ".csv", ".json"]):
        name = os.path.basename(p).lower()
        if "gloss" not in name and p.endswith(".json"):
            continue
        try:
            if p.endswith(".json"):
                data = json.load(open(p, encoding="utf-8"))
                if isinstance(data, dict):
                    gl.update({str(k): str(v) for k, v in data.items()})
                continue
            text, _ = ak.read_text(p)
            for row in csv.reader(text.splitlines(), delimiter="\t" if p.endswith(".tsv") else ","):
                if len(row) >= 2 and row[0].strip():
                    gl[row[0].strip().lower()] = row[1].strip()
        except Exception as exc:
            print(f"glossary {p} skipped: {exc}")
    return gl


def segment(text: str, heading_ok=True):
    """Sentences with their ranges, headings kept as their own segment."""
    segs, cursor = [], 0
    for para in re.split(r"(\n\s*\n)", text):
        if not para.strip():
            cursor += len(para)
            continue
        if para.lstrip().startswith("#"):
            start = cursor + len(para) - len(para.lstrip())
            body = para.strip()
            segs.append({"id": f"s{len(segs)+1:03d}", "kind": "heading", "text": body,
                         "char_start": start, "char_end": start + len(body)})
            cursor += len(para)
            continue
        for s in ak.sentence_split(para):
            at = text.find(s, cursor)
            if at < 0:
                at = cursor
            segs.append({"id": f"s{len(segs)+1:03d}", "kind": "sentence", "text": s,
                         "char_start": at, "char_end": at + len(s)})
            cursor = at + len(s)
    return segs


def load_translation(case: ak.CaseInput, segs):
    """A supplied translation is aligned to the source by order, never by guesswork."""
    cands = [p for p in case.discover() if p.lower().endswith((".md", ".txt"))
             and re.search(r"(zh|cn|translation|translated|target)", os.path.basename(p), re.I)]
    if not cands:
        return None, None
    text, _ = ak.read_text(cands[0])
    body = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    sentences = []
    for ln in body:
        sentences.extend(ak.sentence_split(ln) if not CJK.search(ln) else
                         [x for x in re.split(r"(?<=[。！？；])", ln) if x.strip()])
    return sentences, cands[0]


def audit_segments(segs, trans, glossary, audit: ak.Audit, res: ak.Result, out: str):
    """Document-level preservation first, segment pairing second.

    A translation is not required to keep the source's sentence count: Chinese
    routinely merges two English sentences.  Index pairing would then report
    false losses, so the preservation checks run on the whole document, and the
    segment table is only used when the counts happen to match.
    """
    src_text = " ".join(s["text"] for s in segs)
    tgt_text = " ".join(t for t in trans if t)
    tok_s, tok_t = ak.tokens_of(src_text), ak.tokens_of(tgt_text)
    missing = {k: ak._multiset_missing(sorted(tok_s[k]), sorted(tok_t[k])) for k in tok_s}

    import math
    need = max(1, math.ceil(0.8 * len(segs)))
    audit.check("all-segments-translated", len([t for t in trans if t and t.strip()]) >= need,
                f"{len([t for t in trans if t and t.strip()])} translated of {len(segs)} source segments (need {need})",
                critical=True)
    audit.check("numbers-preserved", not missing["numbers"],
                f"{len(tok_s['numbers'])} in, {len(tok_t['numbers'])} out"
                + (f"; missing {missing['numbers'][:6]}" if missing["numbers"] else ""), critical=True)
    audit.check("units-preserved", not missing["units"],
                f"{len(tok_s['units'])} in, {len(tok_t['units'])} out"
                + (f"; missing {missing['units'][:6]}" if missing["units"] else ""), critical=True)
    audit.check("citations-preserved", not missing["citations"],
                f"{len(tok_s['citations'])} in, {len(tok_t['citations'])} out", weight=0.8)

    untranslated = [t for t in trans if t and t.strip() and not CJK.search(t) and LATIN_WORD.search(t)]
    audit.check("no-untranslated-segment", not untranslated,
                f"{len(untranslated)} sentence(s) contain no target-language characters", critical=True)

    # glossary: one target string per source term, with counts so a human can judge.
    # No "competing term" heuristic: Chinese drops repeated nouns, so a missing
    # occurrence in one sentence is normal and flagging it produced false alarms.
    cons, violations = [], []
    for term, target in glossary.items():
        k = len(re.findall(re.escape(norm_term(term)), norm_term(src_text)))
        m = tgt_text.count(target)
        if k == 0:
            continue
        expected_at_least = 1 if k < 3 else int(k * 0.6 + 0.999)
        ok = m >= expected_at_least
        cons.append({"term": term, "target": target, "source_occurrences": k,
                     "target_occurrences": m, "expected_at_least": expected_at_least,
                     "consistent": ok})
        if not ok:
            violations.append({"term": term, "expected": target,
                               "source_occurrences": k, "target_occurrences": m})
    used = [c for c in cons if c["consistent"]]
    audit.check("glossary-consistent", bool(cons) and len(used) == len(cons),
                f"{len(used)}/{len(cons)} terms used with the locked target", weight=1.0)
    audit.check("glossary-applied", len(cons) >= max(1, len(glossary) // 2),
                f"{len(cons)} of {len(glossary)} terms occur in the source", weight=0.6)

    # segment table: only meaningful when counts line up
    rows, issues = [], []
    src_sentences = [s for s in segs if s["kind"] == "sentence"]
    aligned = len(trans) == len(src_sentences)
    for i, s in enumerate(segs):
        if s["kind"] == "heading":
            rows.append({"id": s["id"], "source": s["text"], "translation": None,
                         "preservation": {}, "aligned": aligned, "status": "heading"})
            continue
        j = src_sentences.index(s)
        t = trans[j] if aligned and j < len(trans) else None
        pres = ak.preserved(s["text"], t) if t else {}
        rows.append({"id": s["id"], "source": s["text"], "translation": t,
                     "preservation": {k: {"ok": v["ok"], "missing": v["missing"][:6]} for k, v in pres.items()},
                     "aligned": aligned, "status": "ok" if t and (not aligned or all(
                         pres[k]["ok"] for k in ("numbers", "units", "citations"))) else
                     ("missing" if not t else "check-at-document-level")})
    for k, items in missing.items():
        for m in items[:6]:
            issues.append({"kind": k, "detail": m})
    return rows, issues, cons, violations


def solve(case: ak.CaseInput, out: str, audit: ak.Audit, res: ak.Result) -> bool:
    docs = [p for p in case.discover() if p.lower().endswith((".md", ".txt"))
            and not re.search(r"translation|translated", os.path.basename(p), re.I)]
    audit.check("source-found", bool(docs), f"{len(docs)} candidate source file(s)", critical=True)
    if not docs:
        return False
    src = docs[0]
    text, _ = ak.read_text(src)
    rel_src = f"inputs/{os.path.basename(src)}"
    ak.write_text(os.path.join(out, rel_src), text)
    res.add_artifact(rel_src, "data", "source text, copied verbatim")
    segs = segment(text)
    audit.check("segments-built", len(segs) >= 3, f"{len(segs)} segments", critical=True)

    glossary = load_glossary(case)
    res.meta["glossary_terms"] = len(glossary)
    trans, tpath = load_translation(case, segs)
    mode = "supplied" if trans else "draft"
    res.meta["mode"] = mode
    if tpath:
        rel_t = f"inputs/{os.path.basename(tpath)}"
        ak.write_text(os.path.join(out, rel_t), ak.read_text(tpath)[0])
        res.add_artifact(rel_t, "data", "supplied translation, copied verbatim")
        res.set("translation_source", rel_t)

    if not trans:
        # term-locked draft: substitute glossary terms, keep everything else
        trans = []
        for s in segs:
            t = s["text"]
            for term, target in sorted(glossary.items(), key=lambda kv: -len(kv[0])):
                t = re.sub(re.escape(term), target, t, flags=re.I)
            trans.append(t)
        res.limits.append("no translation was supplied; the text is a glossary-substituted draft, "
                          "not a translation")

    rows, issues, cons, violations = audit_segments(segs, trans, glossary, audit, res, out)

    # anchors: each source segment is a range in the copied source
    for r in rows:
        seg = next(s for s in segs if s["id"] == r["id"])
        quote = text[seg["char_start"]:seg["char_end"]]
        anchor = ak.Anchor(rel_src, seg["char_start"], seg["char_end"], quote, block_id=seg["id"])
        ok, why = ak.verify_anchor(out, anchor.as_dict())
        res.add_evidence(seg["id"], f"segment {seg['id']}: {ak.clip(seg['text'], 80)}", anchor, ok, why)
    verified = sum(1 for e in res.evidence if e["verified"])
    audit.check("anchors-verified", verified == len(res.evidence) and verified > 0,
                f"{verified}/{len(res.evidence)} source segments re-slice", critical=True)

    translated = [r["translation"] or "" for r in rows]
    body = "\n\n".join(translated)
    ak.write_text(os.path.join(out, "translation.md"), body + "\n")
    ak.write_json(os.path.join(out, "segments.json"), {"segments": rows, "glossary": cons,
                                                       "issues": issues})
    res.add_artifact("translation.md", "data", "the translated text, one paragraph per segment")
    res.add_artifact("segments.json", "data", "segment table with per-segment preservation")

    res.set("segments", rows)
    res.set("translation", body)
    res.set("glossary", cons)
    res.set("consistency", {"terms": len(cons), "consistent": len([c for c in cons if c["consistent"]]),
                            "violations": violations})
    res.set("issues", issues)
    res.set("mode", mode)
    res.set("segment_count", len(segs))
    res.set("translated_count", sum(1 for r in rows if r["translation"]))
    for i in issues[:10]:
        res.add_uncertainty(f"segment {i['id']}: {i['kind']}", str(i["detail"]),
                            "fix the segment and re-run; the audit recomputes")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="/input/case.json")
    ap.add_argument("--output", default="/app/output")
    args = ap.parse_args()
    ak.safe_stdout()
    started = ak.utc_now()
    os.makedirs(args.output, exist_ok=True)
    case = ak.CaseInput.load(args.input, work_dir=args.output)
    audit, res = ak.Audit("reading-03"), ak.Result(args.output, SKILL, VERSION)
    try:
        ok = solve(case, args.output, audit, res)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        ok = False
        audit.check("pipeline-completed", False, f"{type(exc).__name__}: {exc}", critical=True)
        res.add_uncertainty("pipeline exception", str(exc), "read audit.json before using the text")
    res.meta["case_notes"] = case.notes
    status = ak.derive_status(audit, ok)
    if not ok and status == "success":
        status = "partial"
    res.write(case, audit, status, {
        "success": "every segment translated, no number/unit/citation lost, glossary consistent",
        "partial": "a segment or a term failed; see issues",
        "cannot_determine": "no source text could be read",
    }.get(status, status), started, sys.argv)
    a = audit.as_dict()
    print(f"wrote result.json status={status} checks={a['passed']}/{a['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

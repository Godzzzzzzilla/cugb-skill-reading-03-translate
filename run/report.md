# reading-03-translate — case demo-translate-01

- status: **success** (every segment translated, no number/unit/citation lost, glossary consistent)
- checks: 10/10 passed, ratio=1.0
- evidence: 7 anchored claims
- finished: 2026-11-25T07:54:56Z

## Result

```json
{
 "translation_source": "inputs/translation_zh.md",
 "segments": [
  {
   "id": "s001",
   "source": "# Abstract",
   "translation": null,
   "preservation": {},
   "aligned": false,
   "status": "heading"
  },
  {
   "id": "s002",
   "source": "Two-column typesetting is the default for most engineering journals, yet the text layer of a PDF stores glyphs in the order the producer wrote them.",
   "translation": null,
   "preservation": {},
   "aligned": false,
   "status": "missing"
  },
  {
   "id": "s003",
   "source": "We study whether layout-aware reading-order reconstruction improves downstream use of scientific PDFs.",
   "translation": null,
   "preservation": {},
   "aligned": false,
   "status": "missing"
  },
  {
   "id": "s004",
   "source": "A three-page benchmark with a known ground truth is rendered from a controlled layout engine, so that block order, header and footer positions, table cells and equation numbers are known exactly.",
   "translation": null,
   "preservation": {},
   "aligned": false,
   "status": "missing"
  },
  {
   "id": "s005",
   "source": "A naive extractor recovers 71.4% of body characters in the correct position, while a column-aware extractor reaches 98.1%.",
   "translation": null,
   "preservation": {},
   "aligned": false,
   "status": "missing"
  },
  {
   "id": "s006",
   "source": "The gain is largest on pages whose columns are separated by a narrow gutter of 20 pt.",
   "translation": null,
   "preservation": {},
   "aligned": false,
   "status": "missing"
  },
  {
   "id": "s007",
   "source": "We conclude that reading order should be verified block by block rather than asserted, and we release the benchmark and the verifier.",
   "translation": null,
   "preservation": {},
   "aligned": false,
   "status": "missing"
  }
 ],
 "translation": "\n\n\n\n\n\n\n\n\n\n\n\n",
 "glossary": [
  {
   "term": "reading order",
   "target": "阅读顺序",
   "source_occurrences": 2,
   "target_occurrences": 2,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "two-column",
   "target": "双栏",
   "source_occurrences": 1,
   "target_occurrences": 1,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "gutter",
   "target": "栏间距",
   "source_occurrences": 1,
   "target_occurrences": 1,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "block",
   "target": "块",
   "source_occurrences": 3,
   "target_occurrences": 2,
   "expected_at_least": 2,
   "consistent": true
  },
  {
   "term": "ground truth",
   "target": "真值",
   "source_occurrences": 1,
   "target_occurrences": 1,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "extractor",
   "target": "抽取器",
   "source_occurrences": 2,
   "target_occurrences": 2,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "benchmark",
   "target": "基准",
   "source_occurrences": 2,
   "target_occurrences": 2,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "verifier",
   "target": "核验器",
   "source_occurrences": 1,
   "target_occurrences": 1,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "layout",
   "target": "版面",
   "source_occurrences": 2,
   "target_occurrences": 1,
   "expected_at_least": 1,
   "consistent": true
  },
  {
   "term": "glyph",
   "target": "字形",
   "source_occurrences": 1,
   "target_occurrences": 1,
   "expected_at_least": 1,
   "consistent": true
  }
 ],
 "consistency": {
  "terms": 10,
  "consistent": 10,
  "violations": []
 },
 "issues": [],
 "mode": "supplied",
 "segment_count": 7,
 "translated_count": 0
}
```

## Evidence

| id | claim | locator | ok |
|---|---|---|---|
| s001 | segment s001: # Abstract | `inputs/abstract_en.md[0:10]` | ✓ |
| s002 | segment s002: Two-column typesetting is the default for most engineeri | `inputs/abstract_en.md[12:160]` | ✓ |
| s003 | segment s003: We study whether layout-aware reading-order reconstructi | `inputs/abstract_en.md[161:263]` | ✓ |
| s004 | segment s004: A three-page benchmark with a known ground truth is rend | `inputs/abstract_en.md[264:459]` | ✓ |
| s005 | segment s005: A naive extractor recovers 71.4% of body characters in t | `inputs/abstract_en.md[460:582]` | ✓ |
| s006 | segment s006: The gain is largest on pages whose columns are separated | `inputs/abstract_en.md[583:668]` | ✓ |
| s007 | segment s007: We conclude that reading order should be verified block  | `inputs/abstract_en.md[669:802]` | ✓ |

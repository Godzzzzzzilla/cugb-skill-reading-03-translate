---
name: paper-translation
description: Translate a paper section against a locked glossary and audit the result — every sentence accounted for, no number, unit or citation lost, no sentence left in the source language. Use when asked to translate a paper, or to check a translation someone else produced.
---

# Translation with a locked glossary and a real audit

Terminology tables are the easy half. The half that decides quality is whether a
decimal survived, whether a sentence disappeared, and whether one sentence was
left untranslated in the middle of a paragraph. This skill does both halves and
computes the second.

## One command

**Where to run it.** The scripts resolve their own paths, so they work from
any working directory. If your shell starts in `/app/work` (the contract's work
directory), call the absolute path of the script —
`python3 /skills/weekly-skill/scripts/run.py --input /input/case.json --output /app/output`
— or `cd` into the folder holding this `SKILL.md` first and use the relative form
below.

```bash
python3 scripts/run.py --input /input/case.json --output /app/output
```

## Inputs it looks for

| file | role |
|---|---|
| the first non-translation `.md`/`.txt` | the source |
| `glossary.tsv` / `.csv` / `.json` | source term → target term |
| a file matching `translation|translated|zh|cn` | the translation to audit |

With no translation file the skill emits a glossary-substituted **draft**
(`mode: draft`) and says so; it never presents a draft as a translation.

## What it writes

`translation.md` (the text), `segments.json` (segment table, glossary, issues),
`result.json` (`segments`, `translation`, `glossary`, `consistency`, `issues`, `mode`).

## The audit

| check | rule |
|---|---|
| `all-segments-translated` | at least 80% of source segments have a counterpart (ceil, not floor) |
| `numbers-preserved` | the document's number multiset is identical |
| `units-preserved` | the document's unit multiset is identical |
| `citations-preserved` | the `[n]` multiset is identical |
| `no-untranslated-segment` | no target sentence is Latin-only |
| `glossary-consistent` | each source term's locked target appears at least ⌈0.6·k⌉ times for k occurrences |

Preservation is checked **document-wide**, because Chinese legitimately merges two
English sentences; index pairing would report losses that never happened. The
segment table is populated only when the counts line up, and says so via
`aligned`.

## Why no "competing term" rule

An earlier version flagged a sentence whenever a term's target was missing but
another glossary target was present. On a real translation that fired on almost
every sentence, because sentences legitimately contain several glossary terms.
The rule was removed: counts plus a floor catch actual drift, and do not cry wolf.

## Failure handling

| situation | behaviour |
|---|---|
| translation shorter than the source | `all-segments-translated` fails, counts reported |
| decimal altered | `numbers-preserved` fails, missing tokens named |
| sentence left in English | `no-untranslated-segment` fails |
| no glossary | consistency checks are skipped, the rest still runs |
| no source text | `cannot_determine` |

## Limits

- It does not judge fluency or fidelity of meaning; it judges what can be counted.
- Chinese word order and ellipsis mean a term's count can legitimately drop;
  the floor is 60%, not 100%.
- Numbers written as Chinese numerals (`百分之七十一`) are not matched.

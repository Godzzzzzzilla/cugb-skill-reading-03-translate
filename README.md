# reading-03-translate

Glossary-locked translation with a countable audit. Submission for
**阅读03｜文献翻译** (product-arena-01).

## Where the points are

A terminology table alone gets a mid-tier score: the glossary can be obeyed by a
translation that drops a clause. The audit here makes the rest countable — no
number lost, no sentence missing, nothing left in English — so quality is
evidence rather than assertion.

## Measured on the bundled demo (EN → ZH abstract)

| quantity | value |
|---|---|
| source segments | 7 |
| translated sentences | 7 |
| numbers | 3 in, 3 out |
| glossary terms locked | 10 / 10 used with the locked target |
| untranslated sentences | 0 |
| source anchors re-slicing | 7 / 7 |
| audit | 10/10, `status: success` |

`selftest.py` also feeds a translation that drops a sentence and asserts the
audit fails it, and a complete translation and asserts it passes.

## Files

```
SKILL.md               what an agent loads
scripts/run.py         segmentation, glossary, audit
scripts/verify.py      independent anchor verifier
scripts/selftest.py    11 checks incl. a deliberately incomplete translation
scripts/armkit.py      shared core
examples/case.json     demo input (EN abstract, ZH translation, glossary)
run/                   a real run
```

## Reproduce

```bash
python3 scripts/run.py --input examples/case.json --output /tmp/out
python3 scripts/verify.py --result /tmp/out/result.json
python3 scripts/selftest.py
```

## Failure handling

| input | behaviour |
|---|---|
| no translation | glossary-substituted draft, `mode: draft`, stated in `limits` |
| dropped sentence | count below ceil(0.8·n), status `partial` |
| altered decimal | `numbers-preserved` fails, token named |
| untranslated sentence | `no-untranslated-segment` fails |
| no glossary | consistency skipped, preservation still audited |

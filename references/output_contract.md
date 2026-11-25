# result.json

- `segments[]` — `{id, source, translation, preservation{numbers,units,citations}, aligned, status}`.
  `status` ∈ `ok`, `missing`, `check-at-document-level`, `heading`.
- `translation` — the translated text, one paragraph per segment.
- `glossary[]` — `{term, target, source_occurrences, target_occurrences, expected_at_least, consistent}`.
- `consistency` — `{terms, consistent, violations[]}`.
- `issues[]` — `{kind, detail}` for each missing token or untranslated sentence.
- `mode` — `supplied` or `draft`.
- `segment_count`, `translated_count`.

`status: success` requires: 80% of segments translated, all three token classes
preserved document-wide, no Latin-only sentence, and every glossary term at or
above its floor.

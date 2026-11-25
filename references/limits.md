# Limits

| condition | behaviour |
|---|---|
| Chinese numerals instead of digits | not matched as numbers |
| sentence merged across languages | allowed; document-level checks still apply |
| glossary with one term and many inflections | floor of 60% may fail on very short texts |
| source in a third language | treated the same; only CJK is used for "translated" detection |
| headings | not translated by the pipeline; copied through and marked `heading` |

# Topic 7: Document Ingestion

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Identify exactly which document and data sources the project accepts.

## What this topic requires

PDF, TXT, DOCX, CSV, web pages, database records, or other sources must be confirmed from the implementation rather than assumed.

## Required understanding and workflow

1. List supported file types and sources.
2. Name each loader.
3. Explain the loader output structure.
4. Describe metadata captured.
5. Mark unsupported sources as not implemented.

## Workflow

```text
Source -> loader -> documents/pages/records -> normalized content
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

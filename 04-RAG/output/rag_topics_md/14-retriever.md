# Topic 14: Retriever

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Distinguish the vector database from the retriever that applies search behavior.

## What this topic requires

Document search method, Top-K, filters, metadata filtering, thresholds, hybrid search, and reranking only when implemented.

## Required understanding and workflow

1. Locate retriever construction.
2. Record search parameters.
3. Describe filters and thresholds.
4. Explain returned objects and metadata.
5. Mark unsupported features as not implemented.

## Workflow

```text
Query -> retriever policy -> vector database -> ranked documents
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

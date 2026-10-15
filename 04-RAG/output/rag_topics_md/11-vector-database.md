# Topic 11: Vector Database

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Explain the actual vector database and why it is used.

## What this topic requires

Describe stored vectors, chunks, metadata, IDs, collections or indexes, and the difference between normal database lookups and similarity search.

## Required understanding and workflow

1. Identify the vector technology.
2. Find collection/index configuration.
3. Describe stored records.
4. Explain persistence and lifecycle.
5. Mark absent databases clearly.

## Workflow

```text
Chunk + vector + metadata -> collection/index -> similarity search
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

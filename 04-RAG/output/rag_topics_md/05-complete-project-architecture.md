# Topic 5: Complete Project Architecture

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Show the actual frontend, backend, embedding model, vector database, retriever, prompt builder, and LLM connections.

## What this topic requires

A Mermaid architecture diagram adapted from code, not a generic diagram. Every component must be verified or labeled absent.

## Required understanding and workflow

1. Identify system boundaries.
2. Trace request and response paths.
3. Connect ingestion components separately from query components.
4. Label integrations and configuration points.
5. Mark missing components explicitly.

## Workflow

```text
User <-> frontend <-> API <-> query pipeline <-> retrieval and generation
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

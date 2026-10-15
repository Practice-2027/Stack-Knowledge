# Topic 13: Similarity Search

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Explain query vectors, stored vectors, similarity, distance, ranking, and Top-K.

## What this topic requires

Only claim cosine similarity, Euclidean distance, dot product, or another metric when configuration or code confirms it.

## Required understanding and workflow

1. Embed the user query.
2. Search stored vectors.
3. Rank candidates.
4. Select Top-K results.
5. Explain what K means and what happens when results are weak.

## Workflow

```text
User query -> query vector -> vector search -> ranked Top-K chunks
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

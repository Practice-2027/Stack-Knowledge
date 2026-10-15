# Topic 3: What Is RAG?

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Break Retrieval-Augmented Generation into retrieval, augmentation, and generation.

## What this topic requires

Retrieval finds useful source chunks; augmentation adds them to the prompt; generation asks the LLM to produce the response.

## Required understanding and workflow

1. Convert the question into a searchable representation.
2. Find relevant document chunks.
3. Add those chunks to the prompt.
4. Call the LLM.
5. Return a grounded answer.

## Workflow

```text
Question -> embedding -> search -> chunks -> augmented prompt -> LLM -> answer
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

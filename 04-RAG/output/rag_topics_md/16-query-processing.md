# Topic 16: Query Processing

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Explain what happens when a user asks a question, from request intake through the answer.

## What this topic requires

The source text stops mid-topic here, so the complete request/response fields and exact query workflow still need the missing continuation and repository inspection.

## Required understanding and workflow

1. Trace the request into the backend.
2. Identify validation and preprocessing.
3. Create the query embedding if implemented.
4. Retrieve and assemble context.
5. Build the prompt, call the LLM, and return the response.
6. Record the exact request and response formats from code.

## Workflow

```text
User question -> API request -> query processing -> retrieval -> prompt -> LLM -> API response
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

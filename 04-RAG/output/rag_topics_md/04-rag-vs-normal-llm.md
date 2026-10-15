# Topic 4: RAG vs Normal LLM

> Source basis: the pasted “SIMPLE RAG PROJECT — COMPLETE DOCUMENTATION PROMPT”. This file explains the documentation requirement; it does not claim that the repository implements any feature until code inspection confirms it.

## In plain words

Compare an LLM answering from learned knowledge with a RAG system that retrieves current or private context.

## What this topic requires

The comparison must cover hallucinations, knowledge limits, private data, changing information, domain specificity, advantages, and disadvantages.

## Required understanding and workflow

1. Describe the normal LLM path.
2. Describe the RAG path.
3. Compare grounding, freshness, complexity, and cost.
4. Explain that retrieval improves evidence access but does not guarantee truth.
5. Document trade-offs.

## Workflow

```text
Normal: user -> LLM -> answer | RAG: user -> retriever -> context -> LLM -> answer
```

## Evidence rule

- Inspect the repository and cite the relevant file or configuration before describing implementation behavior.
- If a feature is missing, write `NOT IMPLEMENTED IN THIS PROJECT`.
- If it is only a recommendation, write `PRODUCTION RECOMMENDATION - NOT CURRENTLY IMPLEMENTED`.

## Output expectation

The finished project documentation should explain this topic from beginner level through engineering-level detail, with concrete examples derived from the actual code.

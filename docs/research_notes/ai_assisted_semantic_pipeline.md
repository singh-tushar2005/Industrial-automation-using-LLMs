# AI-Assisted Semantic Pipeline

This repository is intended to become both a working migration system and a
research platform for AI-assisted industrial automation analysis.

## Why A Structured Knowledge Base Helps

AI tools perform better when project knowledge is organized. These docs give AI
assistants durable context about:

- architecture boundaries
- compiler concepts
- IEC 61131-3 parsing
- semantic analysis
- IEC 61499 transformation goals
- future research direction

Keeping this material outside source files lets the code stay clean while still
preserving the reasoning behind design decisions.

## Research Direction

Possible research tasks include:

- generating larger Structured Text datasets
- extracting semantic facts from legacy PLC projects
- comparing AST-based and LLM-based migration strategies
- validating transformed IEC 61499 models
- using LLMs to propose transformation candidates
- using symbolic checks to verify migration correctness

## Principle

AI should assist the compiler pipeline, not replace it. The parser and semantic
passes provide structured, deterministic facts. AI components can use those
facts to guide migration, documentation, review, or transformation suggestions.

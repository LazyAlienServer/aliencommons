# AlienMark

AlienMark is the Markdown engine behind AlienCommons.

This documentation currently describes the syntax that is already implemented in the `packages/alienmark` package.

## What AlienMark Does

AlienMark currently provides:

- Markdown parsing
- AST generation
- HTML rendering
- A direct `markdown -> html` rendering path

## Current Scope

The current implementation focuses on a solid core Markdown subset instead of full CommonMark compatibility.

Supported today:

- headings
- paragraphs
- strong emphasis
- emphasis
- inline code
- links
- fenced code blocks
- blockquotes
- ordered and unordered lists
- horizontal rules

## Read Next

- [Syntax Reference](syntax.md)

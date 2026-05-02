# AlienMark

AlienMark is the Markdown parser and HTML renderer used by AlienCommons.

It provides a small, intentional Markdown subset with a structured AST and a direct Markdown-to-HTML rendering API.

## Installation

AlienMark is published to GitHub Packages.

```sh
npm install @lazyalienserver/alienmark --registry=https://npm.pkg.github.com
```

If you use npm with GitHub Packages regularly, configure the registry once:

```sh
npm config set @lazyalienserver:registry https://npm.pkg.github.com
```

## Usage

```ts
import { parseMarkdown, renderMarkdown } from "@lazyalienserver/alienmark";

const html = renderMarkdown("# Hello");
const ast = parseMarkdown("Use **bold** text.");
```

## API

### `renderMarkdown(markdown, options?)`

Parse Markdown and render it into HTML.

```ts
const html = renderMarkdown("Use **bold** text.");
```

### `parseMarkdown(markdown, options?)`

Parse Markdown and return an AlienMark document AST.

```ts
const ast = parseMarkdown("## Title");
```

### `parse(markdown, options?)`

Lower-level parser API.

### `renderHtml(node)`

Render an AlienMark document or block node into HTML.

## Supported Syntax

AlienMark currently supports:

- headings from `#` to `####`
- paragraphs
- strong emphasis with `**text**` and `__text__`
- emphasis with `*text*` and `_text_`
- inline code with backticks
- links with `[label](url)`
- images with `![alt](url)`
- fenced code blocks with triple backticks
- blockquotes with `>`
- single-level ordered and unordered lists
- horizontal rules with `---`, `***`, or `___`

## Notes

AlienMark is not a full CommonMark implementation. It focuses on the Markdown subset currently needed by AlienCommons.

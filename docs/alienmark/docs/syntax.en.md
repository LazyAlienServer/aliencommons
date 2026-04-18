# Syntax Reference

This page documents the Markdown syntax that AlienMark currently supports.

## Headings

AlienMark supports ATX headings from level 1 to level 6.

Input:

```md
# Heading 1
## Heading 2
### Heading 3
```

Output:

```html
<h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3</h3>
```

## Paragraphs

Non-empty lines that do not match a block syntax are grouped into paragraphs. Consecutive lines are joined with spaces.

Input:

```md
This is the first line
and this is the second line.
```

Output:

```html
<p>This is the first line and this is the second line.</p>
```

## Strong Emphasis

Double asterisks create strong emphasis.

Input:

```md
Use **bold** text.
```

Output:

```html
<p>Use <strong>bold</strong> text.</p>
```

## Emphasis

Single `*` and `_` create emphasis.

Input:

```md
Use *italic* and _also italic_.
```

Output:

```html
<p>Use <em>italic</em> and <em>also italic</em>.</p>
```

## Inline Code

Backticks create inline code.

Input:

```md
Use `const answer = 42`.
```

Output:

```html
<p>Use <code>const answer = 42</code>.</p>
```

## Links

AlienMark supports inline links in Markdown form.

Input:

```md
[AlienCommons](https://example.com)
```

Output:

```html
<p><a href="https://example.com">AlienCommons</a></p>
```

## Fenced Code Blocks

Triple backticks create fenced code blocks. A language name after the opening fence is emitted as a `language-*` class on the `code` tag.

Input:

````md
```ts
const answer = 42;
```
````

Output:

```html
<pre><code class="language-ts">const answer = 42;</code></pre>
```

## Blockquotes

Lines starting with `>` are parsed as blockquotes.

Input:

```md
> This is quoted.
```

Output:

```html
<blockquote><p>This is quoted.</p></blockquote>
```

## Lists

AlienMark currently supports single-level ordered and unordered lists.

### Unordered Lists

Input:

```md
- first
- second
```

Output:

```html
<ul><li><p>first</p></li><li><p>second</p></li></ul>
```

### Ordered Lists

Input:

```md
1. first
2. second
```

Output:

```html
<ol><li><p>first</p></li><li><p>second</p></li></ol>
```

## Horizontal Rules

AlienMark supports `---`, `***`, and `___` as horizontal rules.

Input:

```md
---
```

Output:

```html
<hr />
```

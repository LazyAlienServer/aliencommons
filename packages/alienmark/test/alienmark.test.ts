import { describe, expect, it } from "vite-plus/test";

import { parseMarkdown, renderMarkdown } from "../src/index.js";

describe("alienmark", () => {
  it("renders headings and paragraphs", () => {
    const html = renderMarkdown("# Hello\n\nThis is a paragraph.");

    expect(html).toBe("<h1>Hello</h1><p>This is a paragraph.</p>");
  });

  it("only supports headings from h1 to h4", () => {
    const html = renderMarkdown("#### Supported\n\n##### Not supported");

    expect(html).toBe("<h4>Supported</h4><p>##### Not supported</p>");
  });

  it("renders inline markdown", () => {
    const html = renderMarkdown(
      "Use **bold**, __bold too__, *italic*, `code`, and [links](https://example.com).",
    );

    expect(html).toBe(
      '<p>Use <strong>bold</strong>, <strong>bold too</strong>, <em>italic</em>, <code>code</code>, and <a href="https://example.com">links</a>.</p>',
    );
  });

  it("renders images", () => {
    const html = renderMarkdown(
      'Logo: ![Alien "logo"](https://example.com/logo.png?x=<tag>)',
    );

    expect(html).toBe(
      '<p>Logo: <img src="https://example.com/logo.png?x=&lt;tag&gt;" alt="Alien &quot;logo&quot;" /></p>',
    );
  });

  it("renders code fences, blockquotes, lists, and horizontal rules", () => {
    const markdown = [
      "```ts",
      "const answer = 42;",
      "```",
      "",
      "> quoted",
      "",
      "- first",
      "- second",
      "",
      "---",
    ].join("\n");

    const html = renderMarkdown(markdown);

    expect(html).toBe(
      '<pre><code class="language-ts">const answer = 42;</code></pre><blockquote><p>quoted</p></blockquote><ul><li><p>first</p></li><li><p>second</p></li></ul><hr />',
    );
  });

  it("returns a structured document AST", () => {
    const ast = parseMarkdown("## Title");

    expect(ast.type).toBe("document");
    expect(ast.children[0]).toMatchObject({
      type: "heading",
      depth: 2,
    });
  });
});

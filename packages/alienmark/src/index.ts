import type { DocumentNode, ParseOptions } from "./ast/nodes.js";
import { parse } from "./parser/parse.js";
import { renderHtml } from "./renderer/render-html.js";

export function renderMarkdown(markdown: string, options?: ParseOptions): string {
  return renderHtml(parse(markdown, options));
}

export function parseMarkdown(markdown: string, options?: ParseOptions): DocumentNode {
  return parse(markdown, options);
}

export { parse, renderHtml };
export type * from "./ast/nodes.js";

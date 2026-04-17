import type {
  BlockNode,
  BlockquoteNode,
  CodeBlockNode,
  DocumentNode,
  HeadingNode,
  HorizontalRuleNode,
  ListItemNode,
  ListNode,
  ParagraphNode,
  ParseOptions,
} from "../ast/nodes.js";
import { parseInline } from "./inline.js";

const ORDERED_LIST_RE = /^(\d+)\.\s+(.*)$/;
const UNORDERED_LIST_RE = /^[-*]\s+(.*)$/;

export function parse(markdown: string, options: ParseOptions = {}): DocumentNode {
  const normalized = markdown.replace(/\r\n?/g, "\n");
  const lines = normalized.split("\n");
  const children: BlockNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = prepareLine(getLine(lines, index), options);

    if (!line.trim()) {
      index += 1;
      continue;
    }

    if (isFence(line)) {
      const result = parseCodeBlock(lines, index);
      children.push(result.node);
      index = result.nextIndex;
      continue;
    }

    if (isHorizontalRule(line)) {
      const node: HorizontalRuleNode = { type: "horizontalRule" };
      children.push(node);
      index += 1;
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const markers = headingMatch[1] ?? "";
      const text = headingMatch[2] ?? "";
      const node: HeadingNode = {
        type: "heading",
        depth: markers.length,
        children: parseInline(text.trim()),
      };
      children.push(node);
      index += 1;
      continue;
    }

    if (line.startsWith(">")) {
      const result = parseBlockquote(lines, index, options);
      children.push(result.node);
      index = result.nextIndex;
      continue;
    }

    if (isListLine(line)) {
      const result = parseList(lines, index, options);
      children.push(result.node);
      index = result.nextIndex;
      continue;
    }

    const result = parseParagraph(lines, index, options);
    children.push(result.node);
    index = result.nextIndex;
  }

  return {
    type: "document",
    children,
  };
}

function parseCodeBlock(lines: string[], startIndex: number): { node: CodeBlockNode; nextIndex: number } {
  const openingLine = getLine(lines, startIndex).trim();
  const language = openingLine.slice(3).trim() || null;
  const content: string[] = [];
  let index = startIndex + 1;

  while (index < lines.length && !isFence(getLine(lines, index))) {
    content.push(getLine(lines, index));
    index += 1;
  }

  if (index < lines.length && isFence(getLine(lines, index))) {
    index += 1;
  }

  return {
    node: {
      type: "codeBlock",
      language,
      value: content.join("\n"),
    },
    nextIndex: index,
  };
}

function parseBlockquote(
  lines: string[],
  startIndex: number,
  options: ParseOptions,
): { node: BlockquoteNode; nextIndex: number } {
  const collected: string[] = [];
  let index = startIndex;

  while (index < lines.length) {
    const line = prepareLine(getLine(lines, index), options);

    if (!line.trim()) {
      collected.push("");
      index += 1;
      continue;
    }

    if (!line.startsWith(">")) {
      break;
    }

    collected.push(line.replace(/^>\s?/, ""));
    index += 1;
  }

  return {
    node: {
      type: "blockquote",
      children: parse(collected.join("\n"), options).children,
    },
    nextIndex: index,
  };
}

function parseList(
  lines: string[],
  startIndex: number,
  options: ParseOptions,
): { node: ListNode; nextIndex: number } {
  const firstLine = prepareLine(getLine(lines, startIndex), options);
  const orderedMatch = firstLine.match(ORDERED_LIST_RE);
  const ordered = Boolean(orderedMatch);
  const items: ListItemNode[] = [];
  const start = orderedMatch ? Number(orderedMatch[1] ?? "1") : null;
  let index = startIndex;

  while (index < lines.length) {
    const line = prepareLine(getLine(lines, index), options);

    if (!line.trim()) {
      break;
    }

    const match = ordered ? line.match(ORDERED_LIST_RE) : line.match(UNORDERED_LIST_RE);
    if (!match) {
      break;
    }

    const itemText = (match[ordered ? 2 : 1] ?? "").trim();
    items.push({
      type: "listItem",
      children: [
        {
          type: "paragraph",
          children: parseInline(itemText),
        } satisfies ParagraphNode,
      ],
    });
    index += 1;
  }

  return {
    node: {
      type: "list",
      ordered,
      start,
      items,
    },
    nextIndex: index,
  };
}

function parseParagraph(
  lines: string[],
  startIndex: number,
  options: ParseOptions,
): { node: ParagraphNode; nextIndex: number } {
  const collected: string[] = [];
  let index = startIndex;

  while (index < lines.length) {
    const line = prepareLine(getLine(lines, index), options);

    if (!line.trim()) {
      break;
    }

    if (
      collected.length > 0 &&
      (isFence(line) ||
        isHorizontalRule(line) ||
        line.startsWith(">") ||
        isListLine(line) ||
        /^(#{1,6})\s+/.test(line))
    ) {
      break;
    }

    collected.push(line.trim());
    index += 1;
  }

  return {
    node: {
      type: "paragraph",
      children: parseInline(collected.join(" ")),
    },
    nextIndex: index,
  };
}

function isFence(line: string): boolean {
  return line.trim().startsWith("```");
}

function isHorizontalRule(line: string): boolean {
  const trimmed = line.trim();
  return trimmed === "---" || trimmed === "***" || trimmed === "___";
}

function isListLine(line: string): boolean {
  return ORDERED_LIST_RE.test(line) || UNORDERED_LIST_RE.test(line);
}

function prepareLine(line: string, options: ParseOptions): string {
  if (!options.trimTrailingWhitespace) {
    return line;
  }

  return line.replace(/\s+$/g, "");
}

function getLine(lines: string[], index: number): string {
  return lines[index] ?? "";
}

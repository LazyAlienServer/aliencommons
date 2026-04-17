export type BlockNode =
  | DocumentNode
  | ParagraphNode
  | HeadingNode
  | CodeBlockNode
  | BlockquoteNode
  | ListNode
  | HorizontalRuleNode;

export type InlineNode =
  | TextNode
  | StrongNode
  | EmphasisNode
  | InlineCodeNode
  | LinkNode;

export interface DocumentNode {
  type: "document";
  children: BlockNode[];
}

export interface ParagraphNode {
  type: "paragraph";
  children: InlineNode[];
}

export interface HeadingNode {
  type: "heading";
  depth: number;
  children: InlineNode[];
}

export interface CodeBlockNode {
  type: "codeBlock";
  language: string | null;
  value: string;
}

export interface BlockquoteNode {
  type: "blockquote";
  children: BlockNode[];
}

export interface ListNode {
  type: "list";
  ordered: boolean;
  start: number | null;
  items: ListItemNode[];
}

export interface ListItemNode {
  type: "listItem";
  children: BlockNode[];
}

export interface HorizontalRuleNode {
  type: "horizontalRule";
}

export interface TextNode {
  type: "text";
  value: string;
}

export interface StrongNode {
  type: "strong";
  children: InlineNode[];
}

export interface EmphasisNode {
  type: "emphasis";
  children: InlineNode[];
}

export interface InlineCodeNode {
  type: "inlineCode";
  value: string;
}

export interface LinkNode {
  type: "link";
  url: string;
  children: InlineNode[];
}

export interface ParseOptions {
  trimTrailingWhitespace?: boolean;
}

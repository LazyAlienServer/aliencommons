import type {
  BlockNode,
  DocumentNode,
  InlineNode,
  ListItemNode,
  ListNode,
} from "../ast/nodes.js";

export function renderHtml(node: DocumentNode | BlockNode): string {
  switch (node.type) {
    case "document":
      return node.children.map(renderHtml).join("");
    case "paragraph":
      return `<p>${renderInlineNodes(node.children)}</p>`;
    case "heading":
      return `<h${node.depth}>${renderInlineNodes(node.children)}</h${node.depth}>`;
    case "codeBlock": {
      const className = node.language ? ` class="language-${escapeHtmlAttribute(node.language)}"` : "";
      return `<pre><code${className}>${escapeHtml(node.value)}</code></pre>`;
    }
    case "blockquote":
      return `<blockquote>${node.children.map(renderHtml).join("")}</blockquote>`;
    case "list":
      return renderList(node);
    case "horizontalRule":
      return "<hr />";
  }
}

function renderList(node: ListNode): string {
  const tag = node.ordered ? "ol" : "ul";
  const startAttribute = node.ordered && node.start !== null && node.start !== 1 ? ` start="${node.start}"` : "";
  return `<${tag}${startAttribute}>${node.items.map(renderListItem).join("")}</${tag}>`;
}

function renderListItem(item: ListItemNode): string {
  return `<li>${item.children.map(renderHtml).join("")}</li>`;
}

function renderInlineNodes(nodes: InlineNode[]): string {
  return nodes.map(renderInlineNode).join("");
}

function renderInlineNode(node: InlineNode): string {
  switch (node.type) {
    case "text":
      return escapeHtml(node.value);
    case "strong":
      return `<strong>${renderInlineNodes(node.children)}</strong>`;
    case "emphasis":
      return `<em>${renderInlineNodes(node.children)}</em>`;
    case "inlineCode":
      return `<code>${escapeHtml(node.value)}</code>`;
    case "link":
      return `<a href="${escapeHtmlAttribute(node.url)}">${renderInlineNodes(node.children)}</a>`;
  }
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function escapeHtmlAttribute(value: string): string {
  return escapeHtml(value).replace(/"/g, "&quot;");
}

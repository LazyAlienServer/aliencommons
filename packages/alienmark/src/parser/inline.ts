import type {EmphasisNode, InlineCodeNode, InlineNode, LinkNode, StrongNode, TextNode,} from "../ast/nodes.js";

export function parseInline(input: string): InlineNode[] {
  const nodes: InlineNode[] = [];
  let index = 0;
  let buffer = "";

  const flushText = (): void => {
    if (!buffer) {
      return;
    }

    const textNode: TextNode = {
      type: "text",
      value: buffer,
    };
    nodes.push(textNode);
    buffer = "";
  };

  while (index < input.length) {
    const current = input[index];
    if (current === undefined) {
      break;
    }

    if (input.startsWith("**", index)) {
      const closeIndex = input.indexOf("**", index + 2);

      if (closeIndex !== -1) {
        flushText();
        const strongNode: StrongNode = {
          type: "strong",
          children: parseInline(input.slice(index + 2, closeIndex)),
        };
        nodes.push(strongNode);
        index = closeIndex + 2;
        continue;
      }
    }

    if (current === "*" || current === "_") {
      const closeIndex = input.indexOf(current, index + 1);

      if (closeIndex !== -1) {
        flushText();
        const emphasisNode: EmphasisNode = {
          type: "emphasis",
          children: parseInline(input.slice(index + 1, closeIndex)),
        };
        nodes.push(emphasisNode);
        index = closeIndex + 1;
        continue;
      }
    }

    if (current === "`") {
      const closeIndex = input.indexOf("`", index + 1);

      if (closeIndex !== -1) {
        flushText();
        const inlineCodeNode: InlineCodeNode = {
          type: "inlineCode",
          value: input.slice(index + 1, closeIndex),
        };
        nodes.push(inlineCodeNode);
        index = closeIndex + 1;
        continue;
      }
    }

    if (current === "[") {
      const labelEnd = input.indexOf("]", index + 1);

      if (labelEnd !== -1 && input[labelEnd + 1] === "(") {
        const urlEnd = input.indexOf(")", labelEnd + 2);

        if (urlEnd !== -1) {
          flushText();
          const linkNode: LinkNode = {
            type: "link",
            url: input.slice(labelEnd + 2, urlEnd),
            children: parseInline(input.slice(index + 1, labelEnd)),
          };
          nodes.push(linkNode);
          index = urlEnd + 1;
          continue;
        }
      }
    }

    buffer += current;
    index += 1;
  }

  flushText();
  return mergeAdjacentTextNodes(nodes);
}

function mergeAdjacentTextNodes(nodes: InlineNode[]): InlineNode[] {
  const merged: InlineNode[] = [];

  for (const node of nodes) {
    const previous = merged.at(-1);

    if (node.type === "text" && previous?.type === "text") {
      previous.value += node.value;
      continue;
    }

    merged.push(node);
  }

  return merged;
}

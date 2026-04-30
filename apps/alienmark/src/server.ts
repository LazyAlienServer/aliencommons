import Fastify from "fastify";
import { renderMarkdown } from "alienmark";

interface RenderHtmlBody {
  markdown: string;
}

const DEFAULT_HOST = "0.0.0.0";
const DEFAULT_PORT = 8787;

function readPort(): number {
  const rawPort = process.env.PORT;

  if (!rawPort) {
    return DEFAULT_PORT;
  }

  const port = Number(rawPort);

  if (!Number.isInteger(port) || port <= 0 || port > 65535) {
    throw new Error(`Invalid PORT value: ${rawPort}`);
  }

  return port;
}

function readHost(): string {
  return process.env.HOST || DEFAULT_HOST;
}

const app = Fastify({
  logger: true,
  bodyLimit: 1024 * 1024,
});

app.get("/health", async () => {
  return {
    ok: true,
    service: "alienmark",
  };
});

app.post<{ Body: RenderHtmlBody }>(
  "/render-html",
  {
    schema: {
      body: {
        type: "object",
        required: ["markdown"],
        additionalProperties: false,
        properties: {
          markdown: { type: "string" },
        },
      },
      response: {
        200: {
          type: "object",
          required: ["html"],
          properties: {
            html: { type: "string" },
          },
        },
      },
    },
  },
  async (request) => {
    return {
      html: renderMarkdown(request.body.markdown),
    };
  },
);

const host = readHost();
const port = readPort();

await app.listen({ host, port });

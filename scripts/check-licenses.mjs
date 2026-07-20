import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const read = (path) => readFileSync(resolve(root, path), "utf8");
const assert = (condition, message) => {
  if (!condition) {
    throw new Error(message);
  }
};

const rootLicense = read("LICENSE");
for (const path of [
  "packages/alienmark/LICENSE",
  "packages/drf-std-response/LICENSE",
]) {
  assert(read(path) === rootLicense, `${path} must match the root MIT license`);
}

for (const path of [
  "apps/alienmark/LICENSE",
  "apps/backend/LICENSE",
  "apps/frontend/LICENSE",
]) {
  assert(
    !existsSync(resolve(root, path)),
    `${path} duplicates the root license`
  );
}

const alienmarkPackage = JSON.parse(read("packages/alienmark/package.json"));
assert(
  alienmarkPackage.license === "MIT",
  "packages/alienmark/package.json must declare the MIT license"
);

const drfProject = read("packages/drf-std-response/pyproject.toml");
assert(
  /^license = "MIT"$/mu.test(drfProject),
  "packages/drf-std-response/pyproject.toml must declare the MIT license"
);
assert(
  /^license-files = \["LICENSE"\]$/mu.test(drfProject),
  "packages/drf-std-response/pyproject.toml must include its LICENSE file"
);

const packOutput = execFileSync(
  "npm",
  ["pack", "--dry-run", "--json", resolve(root, "packages/alienmark")],
  {
    encoding: "utf8",
    env: {
      ...process.env,
      npm_config_cache: resolve(tmpdir(), "aliencommons-npm-cache"),
    },
  }
);
const [pack] = JSON.parse(packOutput);
assert(
  pack?.files?.some(({ path }) => /^LICENSE(?:\.|$)/iu.test(path)),
  "The AlienMark npm package must contain a LICENSE file"
);

console.log("License audit passed.");

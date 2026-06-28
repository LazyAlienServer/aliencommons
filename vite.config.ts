import { defineConfig } from "vite-plus";

export default defineConfig({
  staged: {
    "*": "vp check --fix",
  },
  lint: {
    env: {
      browser: true,
      es2024: true,
      node: true,
    },
    ignorePatterns: [
      "**/.nuxt/**",
      "**/.output/**",
      "**/dist/**",
      "**/coverage/**",
    ],
    overrides: [
      {
        files: ["*.test.ts", "*.spec.ts", "test/**/*"],
      },
      {
        files: ["*.config.ts", "nuxt.config.ts", "*.config.js"],
      },
    ],
    plugins: [
      "import",
      "vitest",
      "unicorn",
      "typescript",
      "vue",
      "promise",
      "oxc",
      "import",
      "node",
    ],
    rules: {
      eqeqeq: "error",
      "import/no-cycle": "error",
      "import/no-self-import": "error",
      "no-console": "off",
      "no-debugger": "error",
      "promise/always-return": "warn",
      "promise/no-nesting": "warn",
      "typescript/no-explicit-any": "warn",
      "unicorn/no-null": "warn",
      "vue/no-export-in-script-setup": "error",
      "vue/require-typed-ref": "warn",
      "vue/return-in-computed-property": "error",
      "vue/valid-define-emits": "error",
      "vue/valid-define-props": "error",
      "vue/define-props-declaration": ["error", "type-based"],
      "vite-plus/prefer-vite-plus-imports": "error",
    },
    options: {
      typeAware: true,
      typeCheck: true,
    },
    jsPlugins: [
      {
        name: "vite-plus",
        specifier: "vite-plus/oxlint-plugin",
      },
    ],
  },
  fmt: {
    sortTailwindcss: {
      stylesheet: "./apps/frontend/app/assets/css/main.css",
    },
    printWidth: 80,
    sortPackageJson: false,
    trailingComma: "es5",
    ignorePatterns: [
      "apps/frontend/.nuxt",
      "apps/frontend/.output",
      ".nuxt",
      ".output",
      ".dist",
      "dist",
      "coverage",
      "node_modules",
      ".venv",
      "htmlcov",
      "staticfiles",
      "media",
      "pnpm-lock.yaml",
      "pnpm-workspace.yaml",
      "*.md",
    ],
  },
});

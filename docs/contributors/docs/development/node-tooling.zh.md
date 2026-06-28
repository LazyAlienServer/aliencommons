# Node 工具链

AlienCommons 同时使用三类 Node workspace 工具：

- **pnpm workspaces** 定义包图，并负责依赖安装。
- **Turbo** 按依赖顺序运行跨包任务。
- **Vite+** 提供包内的检查、格式化、测试以及 TypeScript 库/服务构建命令。

它们是分层关系，不是彼此替代。pnpm 回答“有哪些包、它们如何依赖彼此”，Turbo 回答“哪个包的任务必须先于另一个任务运行”，Vite+ 回答“这个包里的 check、format、test 或 pack 具体怎么执行”。

Knip 也作为提示性的维护工具可用。它不替代上面三层，也不是必跑的 `pnpm run check` 门禁。它的职责是在维护者想清理 workspace 时，报告未使用文件、导出、依赖和 catalog 条目。

## 包图

Node workspace 在 `pnpm-workspace.yaml` 中声明：

```yaml
packages:
  - "apps/*"
  - "packages/*"
  - "!packages/drf-std-response"
```

当前相关的 Node 包是：

| 包 | 位置 | 角色 |
| --- | --- | --- |
| `frontend` | `apps/frontend` | Nuxt 4 前端应用 |
| `alienmark-service` | `apps/alienmark` | 内部 Fastify Markdown 渲染服务 |
| `alienmark` | `packages/alienmark` | TypeScript Markdown 解析器和 HTML 渲染器 |

`frontend` 和 `alienmark-service` 都依赖本地 `alienmark` 包：

```json
"alienmark": "workspace:*"
```

这个 `workspace:*` 依赖就是 Node 依赖图的事实来源。pnpm 会在安装时链接本地包，Turbo 也会使用同一个 workspace 图来决定上游任务顺序。

## 任务编排

Turbo 是 workspace 的任务编排器。根目录 `package.json` 暴露聚合命令，例如：

```bash
pnpm run check
pnpm run build
pnpm run test
pnpm run typecheck
```

这些命令会调用 `turbo run ...`，而 `turbo.json` 定义任务依赖关系。例如，`build`、`check`、`test` 和 `typecheck` 都依赖上游包的构建：

```json
"build": {
  "dependsOn": ["^build"],
  "outputs": ["dist/**", ".nuxt/**", ".output/**"]
},
"check": {
  "dependsOn": ["^build"]
}
```

`^build` 表示“先运行 workspace 依赖包的 `build` 任务”。实际效果是：

```text
alienmark#build
  -> frontend#check
  -> alienmark-service#check
```

以及：

```text
alienmark#build
  -> frontend#build
  -> alienmark-service#build
```

这样依赖顺序只需要维护在一个地方，不必在 Make target、CI job 或 Dockerfile 里反复手写“先 build `alienmark`，再 build service”。

## 包内命令

Vite+ 是包内工具。每个 Node 包应尽量暴露一致的基础脚本名：

```json
{
  "check": "vp check",
  "check:fix": "vp check --fix",
  "fmt:check": "vp fmt --check",
  "fmt:fix": "vp fmt",
  "lint:check": "vp lint",
  "lint:fix": "vp lint --fix"
}
```

构建命令仍然使用最适合目标产物的工具：

| 包 | 构建命令 | 原因 |
| --- | --- | --- |
| `frontend` | `nuxt build` | Nuxt 应用构建 |
| `alienmark-service` | `vp pack src/server.ts --format esm --dts false` | ESM Node 服务 bundle |
| `alienmark` | `vp pack` | 带声明文件的 TypeScript 库包 |

所以 Vite+ 不替代 pnpm 或 Turbo。它负责标准化 Turbo 在每个包内部执行的命令。

## 根入口

日常开发和 CI 优先使用根脚本：

```bash
pnpm run check      # 通过 Turbo 运行所有包检查
pnpm run build      # 通过 Turbo 构建所有包
pnpm run test       # 通过 Turbo 运行 JavaScript 测试
pnpm run typecheck  # 通过 Turbo 运行 TypeScript 检查
pnpm run knip       # 提示性的未使用代码和未使用依赖报告
```

如果已经知道具体作用域，直接使用 Turbo filter：

```bash
pnpm turbo run check --filter=frontend
pnpm turbo run build --filter=alienmark
pnpm turbo run check --filter=alienmark-service
```

不要新增类似 `frontend:check` 的根 wrapper 脚本；Turbo 的 filter 语法就是包级作用域接口。

直接使用 `pnpm --filter <name> ...` 仍然适合长期运行的开发服务器：

```bash
pnpm --filter frontend dev
pnpm --filter alienmark-service dev
```

开发服务器是持久任务，通常不需要完整的 workspace 任务图。

Knip 有意与聚合检查分离：

```bash
pnpm run knip         # 报告问题，但仍成功退出
pnpm run knip:strict  # 报告问题，并返回非零退出码
```

默认的提示性命令适合清理、裁剪依赖或大型重构前使用。只有在明确希望未使用代码报告阻塞本地运行时，才使用 strict 命令。

## 维护规则

新增或修改 Node 包时：

1. 把它放在 `pnpm-workspace.yaml` 已包含的路径下。
2. 本地包依赖使用 `workspace:*`。
3. 在适用时添加标准 Vite+ 脚本，例如 `check`、`fmt:check`、`lint:check` 和 `typecheck`。
4. 让根脚本和 Make target 调用 Turbo，而不是手写包之间的依赖顺序。
5. 如果新任务有输出、需要上游构建、是持久任务，或不应被缓存，就更新 `turbo.json`。
6. 如果新的根级 Node 工具文件会影响 Node job，就同步更新 CI path filter。
7. 如果新增了框架入口、生成类型文件，或有意保留的依赖需要被未使用代码审计理解，就更新 `knip.jsonc`。

推荐的心智模型是：

```text
pnpm workspace = 包地图和依赖安装
Turbo          = 跨包任务图
Vite+          = 包内质量检查和构建命令
Knip           = 提示性的未使用代码和依赖审计
```

保持这三层职责分离，可以让 workspace 在增加更多应用和包时更容易扩展。

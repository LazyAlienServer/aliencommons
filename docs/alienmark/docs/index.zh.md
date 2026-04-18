# AlienMark

AlienMark 是 AlienCommons 当前使用的 Markdown 引擎。

这份文档目前描述的是 `packages/alienmark` 包中已经实现的语法能力。

## AlienMark 目前能做什么

AlienMark 当前提供：

- Markdown 解析
- AST 生成
- HTML 渲染
- 直接的 `markdown -> html` 渲染流程

## 当前范围

当前实现的目标是先做好一套稳定的 Markdown 核心子集，而不是一次性完整兼容 CommonMark 的所有细节。

目前已经支持：

- 标题
- 段落
- 粗体
- 斜体
- 行内代码
- 链接
- 围栏代码块
- 引用块
- 有序列表和无序列表
- 分隔线

## 继续阅读

- [语法参考](syntax.md)

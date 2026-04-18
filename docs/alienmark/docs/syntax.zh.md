# 语法参考

本页记录了 AlienMark 当前已经支持的 Markdown 语法。

## 标题

AlienMark 支持 1 到 6 级 ATX 标题。

输入：

```md
# 一级标题
## 二级标题
### 三级标题
```

输出：

```html
<h1>一级标题</h1><h2>二级标题</h2><h3>三级标题</h3>
```

## 段落

没有命中其他块级语法的非空行会被归并为段落。连续多行会用空格连接。

输入：

```md
这是第一行
这是第二行。
```

输出：

```html
<p>这是第一行 这是第二行。</p>
```

## 粗体

双星号用于表示粗体。

输入：

```md
使用 **粗体** 文本。
```

输出：

```html
<p>使用 <strong>粗体</strong> 文本。</p>
```

## 斜体

单个 `*` 或 `_` 用于表示斜体。

输入：

```md
使用 *斜体* 和 _也是斜体_。
```

输出：

```html
<p>使用 <em>斜体</em> 和 <em>也是斜体</em>。</p>
```

## 行内代码

反引号用于表示行内代码。

输入：

```md
使用 `const answer = 42`。
```

输出：

```html
<p>使用 <code>const answer = 42</code>。</p>
```

## 链接

AlienMark 当前支持 Markdown 的内联链接写法。

输入：

```md
[AlienCommons](https://example.com)
```

输出：

```html
<p><a href="https://example.com">AlienCommons</a></p>
```

## 围栏代码块

三个反引号用于表示围栏代码块。若在起始围栏后写语言名，会在 `code` 标签上输出 `language-*` 类名。

输入：

````md
```ts
const answer = 42;
```
````

输出：

```html
<pre><code class="language-ts">const answer = 42;</code></pre>
```

## 引用块

以 `>` 开头的行会被解析为引用块。

输入：

```md
> 这是引用内容。
```

输出：

```html
<blockquote><p>这是引用内容。</p></blockquote>
```

## 列表

AlienMark 当前支持单层的有序列表和无序列表。

### 无序列表

输入：

```md
- 第一项
- 第二项
```

输出：

```html
<ul><li><p>第一项</p></li><li><p>第二项</p></li></ul>
```

### 有序列表

输入：

```md
1. 第一项
2. 第二项
```

输出：

```html
<ol><li><p>第一项</p></li><li><p>第二项</p></li></ol>
```

## 分隔线

AlienMark 当前支持 `---`、`***` 和 `___` 作为分隔线。

输入：

```md
---
```

输出：

```html
<hr />
```

---
title: React
published: 2025-04-25
description: react-ts语法框架基础以及常用生态库使用
tags:
  - 开发框架
  - react
category: 编程基础
draft: false
image: '/violet.png'
---

# react

我原本上手使用的是Vue，尤大大的框架还是厉害的，简单易学，而且数据双向通信很利好开发。但是---当我在做一个项目的时候，发现其涉及的周边设施搭建都是基于react或者服务于react的，我不得已转入react，从此我打开新世界的大门，原本以为，react像外界所说上手难度高会消耗我不少时间。

其实不然，鄙人主攻还是一些算法、服务端的开发，对于函数式编程非常熟悉，并且我很讨厌一些莫名奇妙的条条框框去约束我（如果cpp有非常好的包管理器+统一的编译器+拟人的报错提示+能和历史包袱做一个切分，我绝对不会碰rust-看都不看一眼的那一种），所以当进行jsx开发的时候，我彻底沦陷了，更被在vue中想都不敢想的强大生态彻底折服。vue是谁？分手吧-我已经是react门下的人了。

其实vue也很好，高效和易用性我觉得是其生态下产品的特性，比如slidev、vitepress。但是除非有资本驱动力，我大概率还是使用react作为我的主要web（前端）技术栈。

# 自定义属性-data

## data-* 自定义属性速查

### 基础概念

- **语法**：`data-` 开头，如 `data-user-id`
- **值类型**：字符串（支持中文）
- **访问方式**：
  - `getAttribute('data-name')` → 原始字符串
  - `element.dataset.name` → camelCase 映射（`data-user-id` → `userId`）

### React + TypeScript 类型方案

**1. 原生元素**（直接写，无报错）
```tsx
<div data-name="首页" data-user-id="123">内容</div>
```

**2. 自定义组件转发所有 HTML 属性**（推荐）
```tsx
type Props = React.HTMLAttributes<HTMLDivElement> & {
  title?: string;
};

function Card({ title, children, ...rest }: Props) {
  return <div {...rest}>{children}</div>;
}

// 使用
<Card data-name="卡片" data-testid="card-1" />
```

**3. 精确声明 data 属性**
```tsx
type Props = {
  'data-name'?: string;  // 必须引号
  'data-index'?: string;
};

function Item({ 'data-name': name }: Props) {
  return <div data-name={name} />;
}
```

**4. 按钮/表单元素**
```tsx
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

function Button({ ...rest }: ButtonProps) {
  return <button {...rest} />;
}
```

**5. SVG 元素**
```tsx
type SvgProps = React.SVGAttributes<SVGSVGElement>;
```

### 常见问题
- **报错 "Property 'data-name' does not exist"**：组件 props 类型未扩展 HTML 属性接口
- **dataset 映射**：`data-user-id` → `userId`（特殊字符用 `getAttribute`）
- **中文值**：正常使用，`dataset.name === "首页"`

### 最佳实践
- 属性名保持 ASCII（`data-key`）
- 使用 `React.HTMLAttributes<T>` 快速支持 data-*




![](assets/react/file-20260305163755900.png)



![](assets/react/file-20260305190416268.png)


# 代理


为避免同源访问问题，测试环境的时候把前端的访问服务端的请求代理到服务端的接口进行发送。

但是不代理布局资源，因为代理到后端的效果是从后端获取静态资源文件，但是后端暂时不考虑放置静态页面资源。

不代理布局资源，服务端肯定获取不到，因为没设置任何静态资源供提供，只代理api请求


# number精度问题

主要原因通常是前端发生了截断或精度丢失，而不是请求参数长度限制。

详细解释如下：

1. 前端截断/精度丢失  
- JavaScript 的 Number 类型最大安全整数是 9007199254740991（$2^{53}-1$），超出这个范围的 long 型 id（如 7420961149421110742）会被自动四舍五入，导致尾部变 0。
- 这不是参数长度限制，而是 JS 的数值精度问题。

2. 请求参数长度限制  
- 一般 HTTP 请求参数长度限制远大于 long 型数字长度，不会导致 long id 被截断或补 0。
- 只有在极端情况下（如 URL 超长、服务端限制极小）才会有长度问题，但这和 long id 变 0 无关。

**结论：**  

绝大多数情况下，是前端用 JS Number 处理大整数导致精度丢失，建议前后端都用字符串传递 long 型 id，彻底避免此问题。

- 前端（Web端）：用字符串类型传递和接收 id，避免大整数精度丢失问题。
- 后端（Java等）：用 long/BigInteger 等数值型存储和处理 id，保证高效和准确。

这样做的好处：
1. 避免 JS Number 精度丢失，保证 id 不被篡改。
2. 兼容各种前端框架和后端数据库。
3. 传输和存储都安全可靠。

**建议：**
- 前后端接口文档明确 id 字段为字符串类型。
- 后端序列化时将 long id 转为字符串，反序列化时再转回 long。

这样可以彻底解决大整数 id 在前后端传递中的所有精度和兼容性问题。

# Open-API使用



使用 `openapi-typescript-codegen`比较好，适合`ts`，默认使用客户端AXIOS并且会生成，自动分配多个文件夹目录core、service、models。



`OpenAPI Generator`支持多语言转换，但是输出都是单文件，不好用。

## 使用命令示范

```npm
npx openapi-typescript-codegen --input F:\CODE\GIThub\contracts\city\stage_1\openapi\info.openapi.yaml --output F:\CODE\GIThub\city_front\src\info --client axios
```




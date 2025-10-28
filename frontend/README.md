# UniPulse Asia - Frontend

基于 React + TypeScript + Vite + Tailwind CSS + shadcn/ui 构建的前端应用。

## 技术栈

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 原子化 CSS
- **shadcn/ui** - UI 组件库
- **lucide-react** - 图标库
- **React Router** - 路由管理

## 快速开始

### 1. 安装依赖

```bash
cd frontend
pnpm install
```

### 2. 启动开发服务器

```bash
pnpm dev
```

应用将在 http://localhost:3000 启动

### 3. 构建生产版本

```bash
pnpm build
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 组件
│   │   ├── ui/             # shadcn/ui 基础组件
│   │   ├── layout/         # 布局组件 (Header, Sidebar, RightPanel)
│   │   ├── feed/           # Feed 相关组件
│   │   └── common/         # 通用组件
│   ├── pages/              # 页面
│   ├── routes/             # 路由配置
│   ├── services/           # API 服务和 mock 数据
│   ├── types/              # TypeScript 类型定义
│   ├── lib/                # 工具函数
│   └── assets/             # 静态资源
├── public/                 # 公共资源
└── index.html             # 入口 HTML
```

## 功能特性

- ✅ 响应式三栏布局
- ✅ 顶部导航栏（搜索、通知、消息、用户菜单）
- ✅ 左侧导航栏（主导航 + 语言/主题切换）
- ✅ 中间内容流（发帖框 + Feed 流）
- ✅ 右侧信息栏（学校专区、热门话题、交换项目）
- ✅ 悬浮 AI 助手按钮
- ✅ 点赞交互
- ✅ Tab 切换
- ✅ Mock 数据支持

## 环境变量

创建 `.env.local` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 开发规范

- 使用 TypeScript 严格模式
- 组件使用函数式组件 + Hooks
- 样式使用 Tailwind CSS 原子类
- 遵循 shadcn/ui 组件规范
- 保持组件单一职责原则

## 注意事项

- 端口固定为 3000 (`--strictPort`)
- 所有数据目前使用 mock 数据
- 未来对接后端时，API 调用统一使用 `services/` 目录


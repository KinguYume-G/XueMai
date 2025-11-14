# 🔍 交换项目页面调试指南

## ✅ 已完成的修复

### 1. **添加了完整的调试日志链路**

#### 📍 前端组件 (`ExchangePrograms.tsx`)
```typescript
console.log('🎬 ExchangePrograms 组件渲染')
console.log('📊 当前状态:', { programsCount, loading, error })
console.log('🎯 useEffect 触发 - 准备调用 fetchPrograms')
```

#### 📍 Zustand Store (`useExchangeStore.ts`)
```typescript
console.log('🔄 fetchPrograms 被调用')
console.log('📡 准备调用 API: exchangeApi.getPrograms()')
console.log('✅ API 响应 (经过拦截器处理):', response)
console.log('📦 response 类型:', typeof response)
console.log('📦 response 是数组?', Array.isArray(response))
console.log(`✅ 成功获取 ${programs.length} 个交换项目`)
```

#### 📍 API 服务层 (`exchange.ts`)
```typescript
console.log('📡 exchangeApi.getPrograms 被调用')
console.log('🌐 请求 URL:', url)
console.log('✅ 收到响应:', response)
```

#### 📍 HTTP 客户端 (`client.ts`)
```typescript
console.log('🔍 resolveResponseData - 原始 payload:', payload)
console.log('✅ 提取 payload.data:' / '✅ 直接返回 payload:')
```

---

### 2. **修复了数据提取逻辑**

**问题**：
- `apiClient` 的响应拦截器会自动从 `{ data: [...], paging: {...} }` 中提取 `data` 字段
- Store 原本期望 `response.data`，但实际 `response` 本身就是数组

**解决方案**：
```typescript
// 现在 Store 会智能识别响应格式
if (Array.isArray(response)) {
  // 拦截器已经提取了 data，response 就是数组
  programs = response
} else if (response.data) {
  // 完整响应对象
  programs = response.data
}
```

---

## 🧪 测试步骤

### 第1步：启动前端
```bash
cd frontend
pnpm dev
```

### 第2步：打开浏览器开发者工具
- 按 F12 打开
- 切换到 Console 标签

### 第3步：访问页面
```
http://localhost:5173/exchange-programs
```

### 第4步：检查 Console 日志

**✅ 预期看到的日志顺序**：
```
🎬 ExchangePrograms 组件渲染
📊 当前状态: { programsCount: 0, loading: false, error: null, hasFetchPrograms: true }
🎯 useEffect 触发 - 准备调用 fetchPrograms
🔄 fetchPrograms 被调用
📊 当前筛选条件: { country: '', university: '', ... }
📡 准备调用 API: exchangeApi.getPrograms()
📡 exchangeApi.getPrograms 被调用
🌐 请求 URL: /exchange_programs/
🔗 完整路径: http://127.0.0.1:8000/api/exchange_programs/
🔍 resolveResponseData - 原始 payload: { data: [...], paging: {...} }
✅ 提取 payload.data: [...]
✅ 收到响应: [...]
✅ API 响应 (经过拦截器处理): [...]
📦 response 类型: object
📦 response 是数组? true
✅ 数据格式：response 本身是数组 (拦截器已提取)
✅ 成功获取 4 个交换项目
📋 项目列表前3个: [...]
🎬 ExchangePrograms 组件渲染 (再次渲染，此时 programsCount: 4)
```

### 第5步：检查 Network 标签

**✅ 预期看到**：
- 请求：`GET http://127.0.0.1:8000/api/exchange_programs/`
- 状态：`200 OK`
- 响应：
```json
{
  "data": [
    { "id": 11, "title": "2025春季交换项目", ... },
    { "id": 12, "title": "2025暑期研究项目", ... },
    { "id": 13, "title": "2026秋季交换项目", ... },
    { "id": 14, "title": "2026年度交换项目", ... }
  ],
  "paging": {
    "count": 4,
    "next": null,
    "previous": null,
    "page_size": 20
  },
  "error": null
}
```

### 第6步：检查页面显示

**✅ 预期看到**：
- ✅ 4 张交换项目卡片（2行2列布局）
- ✅ 每张卡片包含：
  - 封面图（200px高）
  - 左上角国旗图标
  - 右上角"即将截止"标签（新加坡和香港项目）
  - 右上角收藏按钮
  - 标题、大学、简介
  - 日期、费用、要求信息
  - 评分和申请数统计
  - 底部双按钮

---

## ❌ 常见问题排查

### 问题 A：没有看到任何 Console 日志

**可能原因**：
1. Console 标签被筛选了
2. 页面没有正确加载

**解决方法**：
```bash
# 1. 清除 Console 筛选器
点击 Console 标签的 "Filter" 输入框，删除所有内容

# 2. 刷新页面
按 Ctrl+R 或 F5

# 3. 检查路由
确保访问的是 /exchange-programs 而不是 /exchange
```

---

### 问题 B：看到日志但没有 API 调用

**可能原因**：
- `fetchPrograms` 没有被调用

**解决方法**：
```bash
# 检查日志中是否有：
"🎯 useEffect 触发"  # 如果没有这条，说明 useEffect 没触发

# 如果没有，检查：
1. 确认组件路由正确
2. 检查是否有 React 错误导致组件卸载
```

---

### 问题 C：API 调用但返回错误

**可能原因**：
1. 后端未启动
2. CORS 问题
3. 认证问题

**解决方法**：
```bash
# 1. 确认后端运行
cd backend
python manage.py runserver
# 应该看到：Starting development server at http://127.0.0.1:8000/

# 2. 直接测试后端
curl http://127.0.0.1:8000/api/exchange_programs/
# 应该返回 JSON 数据

# 3. 检查 Console 中的错误信息
看 "❌ fetchPrograms 错误" 的详细信息
```

---

### 问题 D：API 返回数据但页面仍显示空态

**可能原因**：
- 数据提取逻辑错误
- 数据格式不匹配

**检查日志**：
```
✅ 成功获取 X 个交换项目  # X 应该是 4
📋 项目列表前3个: [...]    # 应该显示项目数据
```

**如果 X = 0**：
- 检查响应数据格式
- 查看 "📦 response 类型" 和 "📦 response 是数组?" 的值
- 可能需要调整 Store 中的数据提取逻辑

---

## 📝 调试检查清单

复制下面的清单，逐项检查：

```
前端环境：
□ pnpm dev 运行成功
□ 浏览器访问 http://localhost:5173/exchange-programs
□ 开发者工具 Console 标签已打开
□ Network 标签已打开

后端环境：
□ python manage.py runserver 运行成功
□ curl 测试返回 4 个项目数据
□ 数据库中有 4 条 ExchangeProgram 记录

Console 日志：
□ 看到 "🎬 ExchangePrograms 组件渲染"
□ 看到 "🎯 useEffect 触发"
□ 看到 "🔄 fetchPrograms 被调用"
□ 看到 "📡 exchangeApi.getPrograms 被调用"
□ 看到 "🔍 resolveResponseData"
□ 看到 "✅ 成功获取 4 个交换项目"

Network 请求：
□ 看到 /exchange_programs/ 请求
□ 状态码 200
□ 响应包含 4 个项目

页面显示：
□ 显示 4 张卡片
□ 卡片布局 2行2列
□ 卡片内容完整显示
```

---

## 🚀 完成后清理

测试成功后，可以移除部分调试日志：

**保留的日志**（用于生产环境调试）：
- `console.error` - 所有错误日志
- Store 中的关键错误

**可移除的日志**（仅开发环境需要）：
- `console.log('🎬 组件渲染')`
- `console.log('📦 response 是数组?')`
- 其他详细的调试日志

---

**祝调试顺利！🎉**

如果遇到问题，请：
1. 复制完整的 Console 日志
2. 截图 Network 标签的请求/响应
3. 说明具体的错误现象

# XueMai AI 前端代码审查报告（阶段1）

**审查时间**: 2025-11-30
**审查范围**: 前端AI聊天功能实现

---

## 📊 执行摘要

### 发现的核心问题

1. **路由信息完全未展示** - 后端返回但前端丢弃
2. **对话历史完全是模拟数据** - 未调用真实API
3. **错误处理不完整** - 仅处理401，其他场景缺失
4. **上下文统计信息未保存** - metadata被丢弃

---

## 🔍 任务1.1：定位聊天组件并检查API响应处理

### 核心组件位置

| 文件 | 作用 | 状态 |
|------|------|------|
| `frontend/src/pages/AIChat/index.tsx` | AI聊天主页面 | ✅ 存在 |
| `frontend/src/hooks/useAIStream.ts` | API调用核心逻辑 | ✅ 存在 |
| `frontend/src/services/api/ai.ts` | AI API定义（旧） | ⚠️ 未使用 |
| `frontend/src/constants/aiTools.ts` | 功能定义 | ✅ 存在 |

### API调用流程

```
用户输入 → AIChat/index.tsx (handleSubmit) 
         → useAIStream.sendMessage()
         → POST /api/ai/chat/stream/
         → 处理SSE流式响应
         → 更新messages状态
```

### 后端返回的数据结构（来自views.py:207）

```json
{
  "type": "metadata",
  "routed_to": "course_query",      // ← 未使用
  "confidence": 0.95,               // ← 未使用
  "method": "keyword"               // ← 未使用
}
```

### 前端实际处理（useAIStream.ts:149-151）

```typescript
if (parsed.type === 'metadata') {
  // 路由元数据
  console.log(`🎯 [useAIStream] 路由到: ${parsed.routed_to}`)  // ← 仅打印，未保存！
}
```

### 🚨 发现的问题

#### 问题1.1：路由元数据被丢弃

- **位置**: `useAIStream.ts:149-151`
- **现状**: 收到metadata后仅console.log，未保存到状态
- **影响**: 用户完全不知道AI使用了哪个功能

#### 问题1.2：消息对象缺少metadata字段

- **位置**: `useAIStream.ts:5-10`
- **现状**: 
```typescript
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  // ❌ 缺少 metadata 字段
}
```

#### 问题1.3：AI响应的统计信息未保存

- **位置**: `useAIStream.ts:168-171`
- **现状**:
```typescript
} else if (parsed.type === 'done') {
  // 完成，可以记录耗时
  console.log(`✅ [useAIStream] AI响应完成，耗时: ${parsed.elapsed_ms}ms，共${parsed.chunks}个片段`)
  // ❌ 仅打印，未保存 elapsed_ms 和 chunks
}
```

---

## 🔍 任务1.2：检查对话历史组件实现状态

### 对话历史显示位置

- **文件**: `frontend/src/pages/AITools/index.tsx:50-74`

### 当前实现（第59-72行）

```typescript
{mockConversationHistory.map((conversation) => (
  <button
    key={conversation.id}
    className="..."
    onClick={() => console.log('Open history:', conversation.id)}  // ← 仅打印！
  >
    <span className="font-medium text-foreground line-clamp-1">
      {conversation.title}
    </span>
    <span className="text-xs text-muted-foreground">
      {conversation.timestamp}
    </span>
  </button>
))}
```

### 模拟数据来源

- **文件**: `frontend/src/types/ai.ts:195-226`
- **数据**: hardcoded的5条假数据

### 🚨 发现的问题

#### 问题2.1：完全使用模拟数据

- **严重性**: P0（最高）
- **现状**: `mockConversationHistory` 是写死的假数据
- **缺失**: 完全没有调用 `GET /api/ai/conversations/`

#### 问题2.2：点击事件未实现

- **现状**: `onClick={() => console.log('Open history:', conversation.id)}`
- **应该**: 跳转到 `/ai-chat/${conversation.id}` 或加载对话消息

#### 问题2.3：缺少创建对话的API调用

- **现状**: 发送消息时未创建对话记录
- **后果**: 对话历史永远是空的（即使有真实API）

#### 问题2.4：缺少删除功能

- **现状**: 无删除按钮
- **后端**: 提供了 `DELETE /api/ai/conversations/${id}/`

---

## 🔍 任务1.3：检查错误处理覆盖范围

### 当前错误处理（useAIStream.ts）

| 场景 | 是否处理 | 处理方式 | 评价 |
|------|---------|---------|------|
| token不存在 | ✅ | 跳转登录（70-74行） | 良好 |
| 401未授权 | ✅ | 跳转登录（96-100行） | 良好 |
| 非200响应 | ✅ | 抛出错误（102-106行） | **仅抛出，未展示** |
| 网络断开 | ✅ | catch捕获（179-185行） | **仅setError，未UI展示** |
| 请求取消 | ✅ | 特殊处理（180-181行） | 良好 |
| 404对话不存在 | ❌ | **未处理** | **缺失** |
| 500服务器错误 | ❌ | **未区分** | **缺失** |
| 空输入 | ✅ | 直接return（35行） | **应禁用按钮** |

### 🚨 发现的问题

#### 问题3.1：错误状态未在UI展示

- **位置**: `useAIStream.ts:30` 定义了 `error` 状态
- **问题**: `AIChat/index.tsx` 未读取和展示 `error`

```typescript
// useAIStream 返回了 error
return {
  messages,
  isStreaming,
  error,          // ← 有这个字段
  sendMessage,
  clearMessages,
  setMessages,
}

// AIChat/index.tsx 未使用
const { messages, isStreaming, sendMessage, setMessages } = useAIStream({
  // ❌ error 未被解构
})
```

#### 问题3.2：网络错误无重试按钮

- **现状**: 错误发生后，用户只能刷新页面
- **应该**: 提供"重试"按钮重新发送消息

#### 问题3.3：空输入验证不直观

- **现状**: 空输入时按钮未禁用
- **实际**: `AIChat/index.tsx:211` 有 `disabled={!inputValue.trim() || isStreaming}`
- **问题**: 但未提示用户为何不能发送

#### 问题3.4：404等HTTP错误未区分

- **现状**: 所有非200响应都是 `HTTP错误: ${status}`
- **应该**: 区分400、404、500等，给出具体提示

---

## 📋 缺失功能清单（按优先级）

### P0（必须修复）

- [ ] **路由信息展示**：在消息下方显示 routed_to、confidence、method
- [ ] **对话历史列表**：调用真实API `GET /api/ai/conversations/`
- [ ] **创建对话API**：发送消息前调用 `POST /api/ai/conversations/`
- [ ] **错误提示UI**：展示error状态给用户

### P1（应该修复）

- [ ] **对话历史点击**：跳转到具体对话
- [ ] **对话历史删除**：调用 `DELETE /api/ai/conversations/${id}/`
- [ ] **网络错误重试**：提供重试按钮
- [ ] **HTTP错误区分**：400/404/500不同提示

### P2（可选优化）

- [ ] **上下文统计**：显示使用了多少条历史消息
- [ ] **Token统计**：显示每次对话的token消耗
- [ ] **置信度可视化**：用颜色标识路由置信度
- [ ] **Markdown渲染**：已实现（ReactMarkdown）

---

## 🎯 修复策略建议

### 策略1：增强Message接口（30分钟）

```typescript
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  
  // 新增：元数据
  metadata?: {
    routed_to?: string
    confidence?: number
    method?: string
    elapsed_ms?: number
    chunks?: number
  }
}
```

### 策略2：实现对话历史（2小时）

1. 创建 `frontend/src/services/api/conversations.ts`
2. 定义接口：
   - `createConversation(ai_function: string)`
   - `getConversations()`
   - `deleteConversation(id: number)`
3. 修改 `AITools/index.tsx` 使用真实API
4. 添加加载状态和空状态

### 策略3：完善错误处理（1.5小时）

1. 在 `AIChat/index.tsx` 读取 `error` 状态
2. 添加Toast组件或ErrorBanner组件
3. 区分不同HTTP状态码
4. 添加重试逻辑

### 策略4：路由信息展示（1小时）

1. 修改 `useAIStream` 保存metadata到消息对象
2. 在 `AIChat/index.tsx` 渲染metadata（可折叠）
3. 添加图标和颜色标识

---

## 📊 API调用缺口对照表

| 后端API | 前端是否调用 | 文件位置 | 状态 |
|---------|------------|---------|------|
| `POST /api/ai/chat/stream/` | ✅ | useAIStream.ts:78 | 已实现 |
| `POST /api/ai/conversations/` | ❌ | - | **缺失** |
| `GET /api/ai/conversations/` | ❌ | - | **缺失** |
| `DELETE /api/ai/conversations/{id}/` | ❌ | - | **缺失** |
| `GET /api/ai/conversations/{id}/messages/` | ❌ | - | **缺失** |
| `POST /api/ai/conversations/{id}/chat/` | ❌ | - | **缺失**（使用stream代替） |

---

## 🔧 技术债务

### 债务1：`services/api/ai.ts` 未使用

- **文件**: `frontend/src/services/api/ai.ts`
- **现状**: 定义了 `aiApi.query`，但实际使用的是 `useAIStream`
- **建议**: 删除或重构为conversations API

### 债务2：重复的AI功能定义

- **文件**: 
  - `frontend/src/types/ai.ts` (aiCategories)
  - `frontend/src/constants/aiTools.ts` (AI_FUNCTIONS)
- **问题**: 两处定义，不一致
- **建议**: 统一使用 `constants/aiTools.ts`

### 债务3：localStorage缓存被强制清除

- **位置**: `AIChat/index.tsx:35`
- **代码**: `localStorage.removeItem(\`ai-chat-${functionId}\`)`
- **问题**: 每次进入都清空，无法恢复对话
- **建议**: 改用后端对话历史API

---

## ✅ 阶段1完成确认

- [x] 定位聊天组件 (`AIChat/index.tsx`, `useAIStream.ts`)
- [x] 检查API响应处理（metadata被丢弃）
- [x] 检查对话历史（完全是假数据）
- [x] 检查错误处理（UI展示缺失）
- [x] 生成缺失功能清单

---

**下一步**: 进入阶段2，按P0 → P1 → P2优先级修复功能







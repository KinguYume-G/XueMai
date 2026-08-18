# 🔧 多轮上下文记忆修复报告

## 问题诊断

### 问题描述
多轮对话功能失败，AI无法记住之前的对话内容。

### 根本原因
1. **前端问题**：`useAIStream` hook中，`conversationId`来自`config`参数，是只读的
2. **状态未更新**：当后端返回新的`conversation_id`时，前端没有更新状态
3. **闭包问题**：`sendMessage`函数使用闭包中的`config?.conversationId`，即使后端创建了新对话，后续消息仍然使用旧的（或undefined）`conversation_id`

### 修复方案

#### 1. 使用`useRef`存储`conversationId`
```typescript
// ✅ 使用ref存储conversationId，确保在闭包中能访问最新值
const conversationIdRef = useRef<number | undefined>(config?.conversationId)

// ✅ 当config.conversationId变化时，更新ref
if (config?.conversationId !== conversationIdRef.current) {
  conversationIdRef.current = config?.conversationId
}
```

#### 2. 在发送请求时使用ref中的值
```typescript
// ✅ 使用ref中的最新conversationId
const currentConversationId = conversationIdRef.current

body: JSON.stringify({
  conversation_id: currentConversationId || null,  // ✅ 使用ref中的值
  // ...
})
```

#### 3. 接收后端返回的`conversation_id`并更新ref
```typescript
if (parsed.type === 'metadata') {
  // ✅ 如果后端返回了新的conversation_id，更新ref
  if (parsed.conversation_id && parsed.conversation_id !== conversationIdRef.current) {
    console.log(`🔄 [useAIStream] 更新conversationId: ${conversationIdRef.current} -> ${parsed.conversation_id}`)
    conversationIdRef.current = parsed.conversation_id
  }
  // ...
}

if (parsed.type === 'done') {
  // ✅ done消息中也包含conversation_id
  if (parsed.conversation_id && parsed.conversation_id !== conversationIdRef.current) {
    console.log(`🔄 [useAIStream] 更新conversationId (done): ${conversationIdRef.current} -> ${parsed.conversation_id}`)
    conversationIdRef.current = parsed.conversation_id
  }
  // ...
}
```

## 修复文件

- `frontend/src/hooks/useAIStream.ts` - 添加`conversationIdRef`并更新逻辑

## 测试步骤

### 测试1：新对话创建
1. 打开课程查询页面：`http://localhost:3000/ai-chat/course_query`
2. 发送第一条消息："APU的计算机课程有哪些"
3. 打开浏览器Console，查看日志：
   - 应该看到：`📤 [useAIStream] 发送 AI 请求: { conversationId: null }`
   - 应该看到：`🔄 [useAIStream] 更新conversationId: undefined -> <新的ID>`

### 测试2：多轮对话
1. 在同一个对话中，发送第二条消息："第一门课的学分是多少"
2. 打开浏览器Console，查看日志：
   - 应该看到：`📤 [useAIStream] 发送 AI 请求: { conversationId: <之前的ID> }`
   - AI应该能理解"第一门课"指的是之前提到的课程

### 测试3：指代理解
1. 发送第三条消息："它的先修课程是什么"
2. AI应该能理解"它"指的是之前提到的课程
3. 如果AI说"不知道你指的是什么"，说明上下文未传递

## 预期结果

✅ **第一条消息**
- 创建新对话
- 后端返回`conversation_id`
- 前端更新`conversationIdRef`

✅ **后续消息**
- 使用相同的`conversation_id`
- 后端加载历史消息（最近10条）
- AI能理解指代关系

✅ **Console日志**
```
📤 [useAIStream] 发送 AI 请求: { conversationId: null }
🔄 [useAIStream] 更新conversationId: undefined -> 26
✅ [useAIStream] AI响应完成

📤 [useAIStream] 发送 AI 请求: { conversationId: 26 }
✅ [useAIStream] AI响应完成
```

## 后端验证

后端已经在以下位置实现了多轮对话支持：

1. **创建/加载对话** (`backend/apps/ai/views.py:174-211`)
   ```python
   if conversation_id:
       conversation = AIConversation.objects.get(id=conversation_id, user=request.user)
       # 加载历史消息
       history_messages = AIMessage.objects.filter(conversation=conversation).order_by('created_at')[:10]
   else:
       # 创建新对话
       conversation = AIConversation.objects.create(...)
   ```

2. **注入历史消息** (`backend/apps/ai/views.py:302-318`)
   ```python
   messages = [{"role": "system", "content": enhanced_system}]
   messages.extend(conversation_history_messages)  # ✅ 历史消息
   messages.append({"role": "user", "content": current_question})
   ```

3. **返回conversation_id** (`backend/apps/ai/views.py:320, 353`)
   ```python
   yield f"data: {json.dumps({'type': 'metadata', 'conversation_id': conversation.id})}\n\n"
   yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation.id})}\n\n"
   ```

## 如果测试仍然失败

### 检查点1：后端日志
查看后端终端，应该看到：
```
[对话管理] 创建新对话: 26, 标题: APU的计算机课程有哪些
[多轮对话] 加载了 2 条历史消息
[消息构建] 总消息数: 4 (system: 1, history: 2, current: 1)
```

### 检查点2：前端Console
应该看到：
- `🔄 [useAIStream] 更新conversationId` 日志
- 后续消息的`conversationId`不为null

### 检查点3：网络请求
打开浏览器DevTools → Network → 查看`/api/ai/chat/stream/`请求：
- 第一条消息：`conversation_id: null`
- 第二条消息：`conversation_id: <数字>`

## 其他可能的问题

### 问题1：后端未返回conversation_id
**症状**：Console中没有`🔄 更新conversationId`日志

**解决**：检查后端代码，确保`metadata`和`done`消息中都包含`conversation_id`

### 问题2：历史消息未加载
**症状**：后端日志显示`[多轮对话] 加载了 0 条历史消息`

**解决**：检查数据库，确认消息已保存到`AIMessage`表

### 问题3：AI不理解指代
**症状**：AI回复"不知道你指的是什么"

**解决**：
1. 检查后端是否真的加载了历史消息
2. 检查历史消息的格式是否正确
3. 检查AI模型的上下文窗口是否足够

---

**修复时间**：2025-11-30  
**修复状态**：✅ 已完成  
**测试状态**：待验证



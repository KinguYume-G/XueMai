# 前端报错修复记录

## 问题描述

前端页面点击AI子功能进入后报错：
```
ReferenceError: Cannot access 'sendMessage' before initialization
```

## 根本原因

在 `frontend/src/hooks/useAIStream.ts` 中，我在错误处理的 `catch` 块中引用了 `sendMessage` 和 `messages`，导致循环依赖：

```typescript
// 错误的代码
} catch (err: any) {
  // ...
  const lastUserMessage = messages.findLast(msg => msg.role === 'user')
  if (lastUserMessage) {
    sendMessage(lastUserMessage.content)  // ← 这里引用了sendMessage
  }
} finally {
  // ...
}, [isStreaming, navigate, messages, sendMessage])  // ← 循环依赖
```

这会导致 `sendMessage` 在初始化完成前被引用。

## 修复方案

移除错误处理中的重试逻辑，保持简单的错误提示：

```typescript
} catch (err: any) {
  if (err.name === 'AbortError') {
    console.log('请求被取消')
  } else {
    console.error('流式请求失败:', err)
    const errorMessage = err.message || '网络连接失败，请重试'
    setError(errorMessage)
    
    // 只显示toast，不再自动重试
    if (errorMessage.includes('网络') || errorMessage.includes('Network')) {
      toast.error('网络连接失败，请检查网络后重试')
    } else {
      toast.error(errorMessage)
    }
  }
} finally {
  setIsStreaming(false)
  abortControllerRef.current = null
}, [isStreaming, navigate])  // 移除messages和sendMessage依赖
```

## 其他修复

### 1. 修复后端URL配置
在 `backend/apps/ai/urls.py` 中，恢复了正确的URL模式，支持Django的同一路径多HTTP方法：

```python
# 对话列表（GET）和创建对话（POST）
path("conversations/", views.ai_conversation_list, name="conversation-list"),
path("conversations/", views.ai_conversation_create, name="conversation-create"),
```

## 测试步骤

1. ✅ 刷新前端页面
2. ✅ 点击AI工具
3. ✅ 选择任意功能（如"课程查询"）
4. ✅ 发送消息测试

## 修复状态

- ✅ 前端初始化错误已修复
- ✅ 后端URL配置已修复
- ⏳ 待测试所有功能

---

**修复时间**: 2025-11-30
**修复文件**: `frontend/src/hooks/useAIStream.ts`, `backend/apps/ai/urls.py`


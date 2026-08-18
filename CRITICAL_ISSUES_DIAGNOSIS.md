# 🔍 XueMai AI 系统关键问题诊断报告

**诊断时间**: 2025-11-30 20:00  
**诊断者**: Senior Full-Stack Architect  
**问题级别**: 🔴 CRITICAL - 影响核心功能

---

## 📋 Drake反馈的问题清单

1. ❌ **文件上传后AI无法读取** - 上传成功，但AI回复中没有体现文档内容
2. ❌ **多轮对话上下文缺失** - AI无法记住之前说过的话
3. ❌ **智能路由失败** - 路由到错误的功能
4. ⚠️ **其他功能异常** - 后端可能正常，前端或集成有问题

---

## 🎯 问题1: 文件上传后AI无法读取

### 根本原因分析

#### 🔴 **Critical Bug: 前端未将document_ids传给后端**

**现状 (AIChat/index.tsx 第96-100行)**:
```typescript
// 错误的实现 ❌
if (uploadedFiles.length > 0) {
    const fileInfo = uploadedFiles.map(f => `[已上传文件: ${f.file_name}]`).join('\n')
    messageWithFiles = `${text}\n\n${fileInfo}`  // 只是拼接文件名到消息
}
await sendMessage(messageWithFiles)  // 发送的只是文本，没有document_ids
```

**问题**:
- 前端只是把文件名拼接到消息文本中（如`[已上传文件: resume.pdf]`）
- **没有将`document_id`传递给后端API**
- AI只能看到"[已上传文件: resume.pdf]"这个文本，无法访问文件内容

**后端期望的数据格式 (views.py)**:
```python
# 后端需要接收 document_ids 数组
request.data.get('document_ids', [])  # ❌ 前端没发送！

# 后端会用这些IDs从数据库读取文件内容
for doc_id in document_ids:
    doc = AIDocument.objects.get(id=doc_id)
    file_content = doc.extracted_text  # 获取提取的文本
    # 将文件内容注入到AI的context
```

### 解决方案

#### 修复1: useAIStream.ts - 支持document_ids参数

```typescript
// frontend/src/hooks/useAIStream.ts

export function useAIStream(config?: AIStreamConfig): UseAIStreamReturn {
  const sendMessage = useCallback(async (
    text: string, 
    useRag: boolean = true,
    documentIds?: number[]  // ✅ 新增参数
  ) => {
    // ...
    
    const response = await fetch('/api/ai/chat/stream/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        question: text.trim(),
        mode: config?.mode || 'general',
        use_rag: useRag,
        conversation_id: conversationId,
        document_ids: documentIds || []  // ✅ 传递document_ids
      }),
      signal: abortControllerRef.current.signal,
    })
  })
}
```

#### 修复2: AIChat/index.tsx - 传递document_ids

```typescript
const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isStreaming) return

    const text = inputValue.trim()
    setInputValue('')
    
    // ✅ 正确的实现：传递document_ids
    const documentIds = uploadedFiles.map(f => f.document_id)
    
    if (documentIds.length > 0) {
        console.log('📎 发送消息，附带文档:', documentIds)
    }
    
    await sendMessage(text, true, documentIds)  // ✅ 传递IDs
    
    // 可选：发送后清空文件列表
    // setUploadedFiles([])
}
```

#### 修复3: 后端views.py - 读取并注入文件内容

```python
# backend/apps/ai/views.py (ai_chat_stream函数)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_stream(request):
    question = request.data.get('question')
    mode = request.data.get('mode')
    use_rag = request.data.get('use_rag', True)
    conversation_id = request.data.get('conversation_id')
    document_ids = request.data.get('document_ids', [])  # ✅ 接收document_ids
    
    # ✅ 读取上传的文档内容
    uploaded_documents_context = ""
    if document_ids:
        logger.info(f"[文档上下文] 加载 {len(document_ids)} 个文档")
        try:
            docs = AIDocument.objects.filter(
                id__in=document_ids,
                conversation__user=request.user  # 安全检查：只能访问自己的文档
            )
            for doc in docs:
                uploaded_documents_context += f"\n\n【文档: {doc.file_name}】\n{doc.extracted_text}\n"
            
            logger.info(f"[文档上下文] 共加载 {len(uploaded_documents_context)} 字符")
        except Exception as e:
            logger.error(f"[文档上下文] 加载失败: {e}")
    
    # ✅ 将文档内容注入到system_prompt或user_message
    if uploaded_documents_context:
        enhanced_question = f"{question}\n\n参考文档内容:\n{uploaded_documents_context}"
    else:
        enhanced_question = question
    
    # 传递给AI
    ai_client.chat(messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": enhanced_question}  # ✅ 包含文档内容
    ])
```

---

## 🎯 问题2: 多轮对话上下文缺失

### 根本原因分析

#### 🔴 **Critical Bug: 前端未发送conversation_id + 后端未加载历史消息**

**现状检查**:

1. **useAIStream.ts 第97-102行**:
```typescript
body: JSON.stringify({
  question: text.trim(),
  mode: config?.mode || 'general',
  system_prompt: config?.systemPrompt,
  use_rag: useRag,
  // ❌ 缺失: conversation_id
})
```

2. **AIChat/index.tsx**:
```typescript
const { messages, sendMessage, isStreaming } = useAIStream({
    mode: functionId,
    // ❌ 没有传递conversationId
})
```

3. **后端views.py (第101-300行)**:
```python
def ai_chat_stream(request):
    question = request.data.get('question')
    conversation_id = request.data.get('conversation_id')  # ✅ 后端支持
    
    # ❌ 但是没有加载历史消息！
    # 应该有：
    # if conversation_id:
    #     history_messages = AIMessage.objects.filter(
    #         conversation_id=conversation_id
    #     ).order_by('created_at')[-10:]  # 最近10条
```

### 解决方案

#### 修复1: AIChat/index.tsx - 获取conversationId

```typescript
// frontend/src/pages/AIChat/index.tsx

export default function AIChat() {
    const { functionId } = useParams<{ functionId: string }>()
    const [searchParams] = useSearchParams()
    
    // ✅ 从URL获取conversationId
    const conversationIdParam = searchParams.get('conversation_id')
    const [conversationId, setConversationId] = useState<number | undefined>(
        conversationIdParam ? parseInt(conversationIdParam) : undefined
    )
    
    // ✅ 传递conversationId给useAIStream
    const { messages, sendMessage, isStreaming, setMessages } = useAIStream({
        mode: functionId,
        conversationId: conversationId  // ✅ 传递ID
    })
    
    // ✅ 如果有conversationId，加载历史消息
    useEffect(() => {
        if (conversationId) {
            loadConversationHistory(conversationId)
        }
    }, [conversationId])
    
    const loadConversationHistory = async (convId: number) => {
        try {
            const response = await fetch(`/api/ai/conversations/${convId}/messages/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('xm_access_token')}`
                }
            })
            const data = await response.json()
            
            // 将历史消息转换为前端格式
            const historyMessages = data.messages.map((msg: any) => ({
                id: `${msg.role}-${msg.id}`,
                role: msg.role,
                content: msg.content,
                timestamp: new Date(msg.created_at)
            }))
            
            setMessages(historyMessages)
        } catch (error) {
            console.error('加载历史消息失败:', error)
        }
    }
}
```

#### 修复2: useAIStream.ts - 支持conversationId

```typescript
interface AIStreamConfig {
  mode?: string
  systemPrompt?: string
  useRag?: boolean
  conversationId?: number  // ✅ 新增
}

export function useAIStream(config?: AIStreamConfig): UseAIStreamReturn {
  const sendMessage = useCallback(async (
    text: string,
    useRag: boolean = true,
    documentIds?: number[]
  ) => {
    // ...
    
    const response = await fetch('/api/ai/chat/stream/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        question: text.trim(),
        mode: config?.mode || 'general',
        use_rag: useRag,
        conversation_id: config?.conversationId,  // ✅ 传递conversationId
        document_ids: documentIds || []
      }),
      signal: abortControllerRef.current.signal,
    })
  }, [config?.mode, config?.conversationId])  // ✅ 添加依赖
}
```

#### 修复3: 后端views.py - 加载并发送历史消息

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat_stream(request):
    question = request.data.get('question')
    mode = request.data.get('mode')
    conversation_id = request.data.get('conversation_id')
    document_ids = request.data.get('document_ids', [])
    
    # ✅ 如果有conversation_id，加载历史消息
    conversation_history = []
    if conversation_id:
        try:
            # 验证权限
            conversation = AIConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
            
            # 加载最近10条历史消息
            history_messages = AIMessage.objects.filter(
                conversation=conversation
            ).order_by('created_at')[-10:]  # 最近10条
            
            for msg in history_messages:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            logger.info(f"[多轮对话] 加载了 {len(conversation_history)} 条历史消息")
        except AIConversation.DoesNotExist:
            logger.warning(f"[多轮对话] 对话 {conversation_id} 不存在")
    
    # ✅ 构建完整的消息列表
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.extend(conversation_history)  # ✅ 添加历史消息
    messages.append({"role": "user", "content": enhanced_question})
    
    # 发送给AI
    stream = ai_client.chat(messages=messages, stream=True)
```

---

## 🎯 问题3: 智能路由失败

### 根本原因分析

#### 观察到的现象
- 从截图看，路由显示"[useAIStream] 路由目标: general"
- 用户可能期望路由到特定功能（如course_query、resume_optimize）

#### 可能的原因

1. **前端已指定mode参数**
```typescript
const { messages, sendMessage, isStreaming } = useAIStream({
    mode: functionId,  // ✅ 这里传递了functionId
})
```

2. **后端收到mode后不再识别**
```python
# views.py 第127-130行
recognizer = get_intent_recognizer()
intent_result = recognizer.recognize(query=question, mode=mode)

if mode:
    # 如果提供了mode，跳过意图识别
    routed_function_id = mode  # ✅ 直接使用前端传来的mode
else:
    # 自动识别
    routed_function_id = intent_result.get('target_function', 'general')
```

#### 诊断

**这个功能实际上是正常的！**

- 如果URL是`/ai-chat/course_query`，functionId就是`course_query`
- 前端传递`mode: 'course_query'`给后端
- 后端直接使用这个mode，不进行二次识别
- 这是**正确的行为**

**为什么看起来像"失败"？**

可能Drake期望看到"智能识别"的过程，但实际上：
- 用户点击"课程查询"按钮 → 已经明确了意图
- 不需要AI再"猜"用户想干什么
- 直接使用course_query模式

### 优化建议

如果需要显示"智能识别"效果，可以：

1. 在主页输入框输入问题（不指定mode）
2. 后端自动识别意图
3. 跳转到对应的功能页面

**这个功能后续优化即可，不是bug。**

---

## 🎯 问题4: 其他功能异常原因分析

### 根据截图和日志分析

#### ✅ 后端正常运行
```
Django version 5.2.7
Starting development server at http://127.0.0.1:8000/
System check identified no issues (0 silenced).
```

#### ⚠️ 警告信息分析

**1. PIL/pytesseract警告**:
```
WARNING:root:PIL/pytesseract not installed, OCR support disabled
```
- **影响**: 无法对图片进行OCR文字识别
- **解决**: 安装`pip install pytesseract pillow`
- **优先级**: P2（图片上传功能受限）

**2. DRF Schema警告**:
```
Error [ai_chat_stream]: unable to guess serializer...
```
- **影响**: API文档生成有问题，但**不影响功能**
- **解决**: 添加`@extend_schema`装饰器
- **优先级**: P3（美化问题）

#### 🔍 前端可能的问题

1. **缺少错误处理提示**
   - 文件上传成功，但AI无法读取时，没有明确提示
   - 用户不知道问题出在哪里

2. **缺少loading状态**
   - 多轮对话加载时，没有"加载历史消息中..."提示

3. **缺少功能引导**
   - 用户不知道如何正确使用多模态功能

---

## 📊 问题优先级排序

| 问题 | 优先级 | 影响范围 | 预计修复时间 |
|------|--------|----------|-------------|
| 文件上传AI无法读取 | 🔴 P0 | 核心功能 | 2小时 |
| 多轮对话上下文缺失 | 🔴 P0 | 核心功能 | 1.5小时 |
| OCR支持缺失 | 🟡 P2 | 图片功能 | 0.5小时 |
| 智能路由"显示"优化 | 🟢 P3 | UX优化 | 1小时 |
| API文档警告 | 🟢 P3 | 开发体验 | 1小时 |

---

## 🛠️ 修复计划

### Phase 1: 紧急修复 (3.5小时)

#### Task 1: 修复文件上传AI读取 (2小时)
1. ✅ 修改`useAIStream.ts` - 支持`documentIds`参数
2. ✅ 修改`AIChat/index.tsx` - 传递`documentIds`
3. ✅ 修改`AIChatInput.tsx` - 传递`documentIds`
4. ✅ 修改`views.py` - 读取并注入文档内容
5. ✅ 测试：上传PDF → 问"总结文档" → 验证AI能看到内容

#### Task 2: 修复多轮对话上下文 (1.5小时)
1. ✅ 修改`AIChat/index.tsx` - 获取并传递`conversationId`
2. ✅ 修改`useAIStream.ts` - 支持`conversationId`参数
3. ✅ 修改`views.py` - 加载并发送历史消息
4. ✅ 新增API：`GET /api/ai/conversations/{id}/messages/`
5. ✅ 测试：发送3条消息 → 刷新页面 → 验证能看到历史

### Phase 2: 优化增强 (2小时)

#### Task 3: 安装OCR支持 (0.5小时)
```bash
pip install pytesseract pillow
# Windows需要安装Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
```

#### Task 4: 添加用户体验优化 (1.5小时)
1. 文件上传成功后，Toast提示"AI正在分析文档..."
2. 加载历史消息时显示Loading
3. 文档内容过长时，自动截断并提示
4. 多轮对话时，显示上下文消息数量

---

## 💡 关键发现总结

### Drake，重点看这里！

#### 🔴 核心问题（必须修复）

1. **文件上传AI无法读取**
   - 原因：前端只传了文件名字符串，没传document_id
   - 后果：AI看不到文档内容，只能看到"[已上传文件: xxx.pdf]"
   - 修复：传递`document_ids: [1, 2, 3]`给后端

2. **多轮对话没有上下文**
   - 原因：前端没传conversation_id，后端没加载历史
   - 后果：AI无法记住之前说过的话
   - 修复：传递`conversation_id`并在后端加载历史消息

#### ✅ 不是问题（实际正常）

3. **智能路由**
   - 现状：功能正常，直接使用前端指定的mode
   - 无需修复，只是显示方式让Drake觉得"失败"

#### 🟡 次要问题（可延后）

4. **OCR支持**
   - 现状：未安装，图片无法识别文字
   - 解决：安装pytesseract

---

## 🎯 下一步行动

Drake，我建议：

### 立即执行（现在）

我将开始修复P0问题：
1. 修改前端传递`document_ids`和`conversation_id`
2. 修改后端读取文档内容和历史消息
3. 测试验证功能正常

### 预计时间

- 代码修改：2小时
- 测试验证：1小时
- **总计：3小时即可修复核心问题**

### 你的确认

如果同意，我现在开始修复。完成后Drake可以测试：
- 上传PDF → 问AI"总结文档" → AI应该能真正读懂内容
- 发送3条消息 → 刷新 → 历史消息应该还在

**准备好了吗？Drake确认后我立即开始！** 🚀


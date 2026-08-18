import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Send, Paperclip, Loader2, X, FileText, Image as ImageIcon, Video } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { getFunctionById } from '@/constants/aiTools'
import { useAIStream } from '@/hooks/useAIStream'
import { uploadFile, type UploadFileResponse } from '@/services/api/upload'
import { conversationsApi } from '@/services/api/conversations'
import { apiFetch, readApiErrorMessage } from '@/lib/api/client'
import { toast } from '@/store/useToastStore'
import WorkflowProgress, { type WorkflowStep } from '@/components/ai/WorkflowProgress'
import { WorkflowResult } from './components/WorkflowResult'

export default function AIChat() {
    const { functionId } = useParams()
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const [inputValue, setInputValue] = useState('')
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const welcomeAddedRef = useRef(false)
    const initialMessageSentRef = useRef(false)

    // ✅ 获取conversationId（从URL或新建）
    const conversationIdParam = searchParams.get('conversation_id')
    const [conversationId] = useState<number | undefined>(
        conversationIdParam ? parseInt(conversationIdParam) : undefined
    )

    console.log('🔍 [AIChat] conversationId初始化:', conversationId, 'URL参数:', conversationIdParam)

    // 文件上传相关状态
    const [uploadedFiles, setUploadedFiles] = useState<UploadFileResponse[]>([])
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Orchestrator工作流相关状态（简化版，使用现有WorkflowStep类型）
    const [orchestratorSteps, setOrchestratorSteps] = useState<WorkflowStep[]>([])
    const [orchestratorResult, setOrchestratorResult] = useState<{ answer: string; metadata?: any } | null>(null)
    const [orchestratorRunning, setOrchestratorRunning] = useState(false)

    const aiFunction = functionId ? getFunctionById(functionId) : null

    // ✅ Initialize AI stream - 传递conversationId
    const {
        messages,
        isStreaming,
        sendMessage,
        setMessages,
        error,
        workflowState,
        conversationId: activeConversationId,
    } = useAIStream({
        mode: functionId,
        useRag: true,
        conversationId: conversationId  // ✅ 传递对话ID
    })

    // 历史消息加载状态
    const historyLoadedRef = useRef(false)

    // Initialization Effect: 清理旧历史 + 生成新欢迎语
    useEffect(() => {
        if (!functionId || !aiFunction) return

        // 重置状态
        welcomeAddedRef.current = false

        // 🛑 核心修改：强制清除当前功能的旧历史缓存
        // 这样不仅不保存，还会把以前有问题的缓存删得干干净净
        localStorage.removeItem(`ai-chat-${functionId}`)

        // 清空当前视图的消息（确保从零开始）
        setMessages([])

        // 生成全新的欢迎消息（带 \n 修复）
        if (!welcomeAddedRef.current) {
            // 修复描述中的转义字符
            const cleanDescription = aiFunction.description
                .replace(/\\n/g, '\n')   // 修复换行
                .replace(/\\t/g, '  ')   // 修复制表符
                .trim();

            setMessages([{
                id: 'welcome',
                role: 'assistant',
                content: `你好！我是${aiFunction.name}助手。\n\n${cleanDescription}\n\n请问有什么我可以帮你的吗？`,
                timestamp: new Date()
            }])
            welcomeAddedRef.current = true
        }
    }, [functionId, aiFunction, setMessages])

    // ✅ 新增：加载历史对话消息
    useEffect(() => {
        const loadConversationHistory = async () => {
            // 只有当有conversationId且未加载过历史时才加载
            if (!conversationId || historyLoadedRef.current) return

            console.log('🔍 [AIChat] 开始加载对话历史, conversation_id:', conversationId)
            historyLoadedRef.current = true
            try {
                const history = await conversationsApi.getMessages(conversationId)
                console.log('✅ [AIChat] 历史消息加载成功:', history.length, '条')

                    // 转换后端格式到前端Message接口
                    const formattedMessages = history.map((msg) => ({
                        id: msg.id.toString(),
                        role: msg.role as 'user' | 'assistant',
                        content: msg.content,
                        timestamp: new Date(msg.created_at)
                    }))

                    // 设置消息（替换欢迎消息）
                    setMessages(formattedMessages)
            } catch (error) {
                console.error('❌ [AIChat] 加载历史异常:', error)
                toast.error('加载历史消息时发生错误')
            }
        }

        loadConversationHistory()
    }, [conversationId, setMessages])

    // 🛑 已删除：保存历史记录的 useEffect
    // 🛑 已删除：读取历史记录的 useEffect
    // 现在每次刷新或重新进入，都是全新的开始

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isStreaming]) // 添加isStreaming依赖，流式时也滚动

    // Handle initial message from URL
    useEffect(() => {
        const initialMessage = searchParams.get('message')
        if (initialMessage && !initialMessageSentRef.current && !isStreaming) {
            initialMessageSentRef.current = true
            setTimeout(() => {
                sendMessage(initialMessage)
            }, 500)
        }
    }, [searchParams, sendMessage, isStreaming])

    // 🆕 Orchestrator工作流执行函数
    const handleOrchestratorChat = async (question: string, documentIds: number[]) => {
        try {
            // 添加用户消息到界面
            const userMessage = {
                id: Date.now().toString(),
                role: 'user' as const,
                content: question,
                timestamp: new Date()
            }
            setMessages(prev => [...prev, userMessage])

            // 重置工作流状态
            setOrchestratorRunning(true)
            setOrchestratorSteps([])
            setOrchestratorResult(null)

            console.log('🚀 [Orchestrator] 开始执行工作流:', { question, documentIds })

            const response = await apiFetch('/ai/orchestrator/execute/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question,
                    document_ids: documentIds,
                    // workflow_name: 'resume_optimization' // 可选，让后端自动匹配
                })
            })

            if (!response.ok) {
                throw new Error(await readApiErrorMessage(response))
            }

            const reader = response.body?.getReader()
            if (!reader) {
                throw new Error('无法获取响应流')
            }

            const decoder = new TextDecoder()
            let buffer = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    if (!line.trim() || !line.startsWith('data: ')) continue

                    const data = line.substring(6).trim()
                    if (data === '[DONE]') {
                        console.log('✅ [Orchestrator] 流式传输完成')
                        continue
                    }

                    try {
                        const event = JSON.parse(data)
                        console.log('📨 [Orchestrator] SSE事件:', event.type, event)

                        switch (event.type) {
                            case 'workflow_start': {
                                console.log(`🔄 [Orchestrator] 工作流开始: ${event.workflow_name}, 共${event.total_steps}步`)
                                // 初始化步骤列表
                                const initialSteps = Array.from({ length: event.total_steps }, (_, i) => ({
                                    id: `step_${i + 1}`,
                                    name: `步骤 ${i + 1}`,
                                    description: '',
                                    status: 'pending' as const
                                }))
                                setOrchestratorSteps(initialSteps)
                                break
                            }

                            case 'step_completed':
                                console.log(`✅ [Orchestrator] 步骤完成: ${event.step_name}`)
                                setOrchestratorSteps((prev: WorkflowStep[]) => prev.map((step: WorkflowStep) =>
                                    step.id === event.step_id || step.name === `步骤 ${event.completed}`
                                        ? { ...step, id: event.step_id, name: event.step_name, status: 'completed' as const, result: event.result || step.result }
                                        : step
                                ))
                                break

                            case 'step_failed':
                                console.error(`❌ [Orchestrator] 步骤失败: ${event.step_name}`, event.error)
                                setOrchestratorSteps((prev: WorkflowStep[]) => prev.map((step: WorkflowStep) =>
                                    step.id === event.step_id
                                        ? { ...step, name: event.step_name, status: 'failed' as const, error: event.error }
                                        : step
                                ))
                                toast.error(`步骤失败: ${event.step_name}`)
                                break

                            case 'workflow_completed':
                                console.log(`🎉 [Orchestrator] 工作流完成! 耗时: ${event.elapsed_ms}ms`)
                                setOrchestratorRunning(false)
                                break

                            case 'workflow_failed':
                                console.error(`💥 [Orchestrator] 工作流失败:`, event.error)
                                setOrchestratorRunning(false)
                                toast.error(`工作流执行失败: ${event.error}`)
                                break

                            case 'final_result':
                                console.log('📋 [Orchestrator] 最终结果:', event.results)
                                if (event.results && event.results.answer) {
                                    setOrchestratorResult(event.results)
                                    // 添加AI回复到消息列表
                                    const aiMessage = {
                                        id: Date.now().toString(),
                                        role: 'assistant' as const,
                                        content: event.results.answer,
                                        timestamp: new Date()
                                    }
                                    setMessages(prev => [...prev, aiMessage])
                                }
                                break

                            case 'error':
                                console.error('❌ [Orchestrator] 错误:', event.message)
                                toast.error(event.message)
                                break
                        }
                    } catch (parseError) {
                        console.error('解析SSE事件失败:', parseError, 'Raw data:', data)
                    }
                }
            }

        } catch (error: any) {
            console.error('🔥 [Orchestrator] 执行失败:', error)
            setOrchestratorRunning(false)
            toast.error(error.message || '工作流执行失败，请重试')
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!inputValue.trim() || isStreaming) return

        const text = inputValue.trim()
        setInputValue('') // 立即清空输入框

        // ✅ 提取文档IDs
        const documentIds = uploadedFiles.map(f => f.document_id)

        // 🆕 智能路由：有文件上传时使用Orchestrator工作流
        if (documentIds.length > 0) {
            console.log('📎 [AIChat] 检测到文件上传，使用Orchestrator工作流')
            console.log('📎 [AIChat] 文档IDs:', documentIds)
            const fileNames = uploadedFiles.map(f => f.file_name).join(', ')
            console.log(`📎 [AIChat] 附件: ${fileNames}`)

            await handleOrchestratorChat(text, documentIds)
        } else {
            // 普通聊天，使用原有API
            console.log('💬 [AIChat] 无附件，使用普通聊天')
            await sendMessage(text, true, documentIds)
        }

        // 可选：发送后清空文件列表（让用户可以继续讨论这些文件）
        // setUploadedFiles([])
    }

    // 处理文件选择
    const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files
        if (!files || files.length === 0) return

        const file = files[0]

        // 验证文件大小（10MB限制）
        const maxSize = 10 * 1024 * 1024
        if (file.size > maxSize) {
            toast.error('文件大小不能超过10MB')
            return
        }

        // 开始上传
        setUploading(true)
        setUploadProgress(0)

        try {
            // 模拟进度（实际应该用XMLHttpRequest获取真实进度）
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => Math.min(prev + 10, 90))
            }, 200)

            // ✅ 传递conversationId（如果有）- undefined转为null
            const result = await uploadFile(file, activeConversationId)

            clearInterval(progressInterval)
            setUploadProgress(100)

            // 添加到已上传文件列表
            setUploadedFiles(prev => [...prev, result])

            toast.success(`文件上传成功: ${result.file_name}`)
            console.log('📎 [文件上传] document_id:', result.document_id, 'conversation_id:', activeConversationId || 'none')

            // ✅ 自动发送分析请求 - 根据功能ID优化提示词
            setTimeout(() => {
                if (functionId === 'resume_optimize') {
                    setInputValue(`请帮我分析这份简历，并给出优化建议`)
                } else if (functionId === 'general') {
                    setInputValue(`请帮我分析这个文件`)
                } else {
                    setInputValue(`请帮我分析这个文件`)
                }
            }, 500)

        } catch (error: unknown) {
            console.error('文件上传失败:', error)
            const errorMessage = error instanceof Error ? error.message : '文件上传失败，请重试'
            toast.error(errorMessage)
        } finally {
            setUploading(false)
            setUploadProgress(0)
            // 清空input以允许重复上传同一文件
            if (fileInputRef.current) {
                fileInputRef.current.value = ''
            }
        }
    }

    // 删除已上传文件
    const handleRemoveFile = (index: number) => {
        setUploadedFiles(prev => prev.filter((_, i) => i !== index))
        toast.success('文件已移除')
    }

    // 打开文件选择对话框
    const handleUploadClick = (fileType: 'image' | 'video' | 'document') => {
        if (!fileInputRef.current) return

        // 设置接受的文件类型
        const acceptMap = {
            image: '.jpg,.jpeg,.png,.gif',
            video: '.mp4,.mov,.avi',
            document: '.pdf,.docx,.doc,.txt,.csv'
        }

        fileInputRef.current.accept = acceptMap[fileType]
        fileInputRef.current.click()
    }

    if (!aiFunction) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="text-center">
                    <h2 className="text-xl font-bold text-gray-900">功能不存在</h2>
                    <button
                        onClick={() => navigate('/ai-tools')}
                        className="mt-4 text-blue-600 hover:underline"
                    >
                        返回工具箱
                    </button>
                </div>
            </div>
        )
    }

    const Icon = aiFunction.icon

    return (
        <div className="flex h-[calc(100vh-4rem)] flex-col bg-gray-50 -m-6">
            {/* Header */}
            <header className="flex h-16 items-center gap-4 border-b bg-white px-6 shadow-sm flex-shrink-0">
                <button
                    onClick={() => navigate('/ai-tools')}
                    className="flex items-center gap-2 text-gray-600 transition-colors hover:text-gray-900"
                >
                    <ArrowLeft className="h-5 w-5" />
                    <span>返回</span>
                </button>
                <div className="h-8 w-px bg-gray-200" />
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                        <Icon className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-gray-900">{aiFunction.name}</h1>
                        <p className="text-xs text-gray-500">{aiFunction.description}</p>
                    </div>
                </div>
            </header>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-6 py-6">
                <div className="mx-auto max-w-3xl space-y-6">
                    {/* 错误提示 */}
                    {error && (
                        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                            <div className="flex-shrink-0 text-red-500">
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-red-800">{error}</p>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, idx) => (
                        <div key={msg.id || idx}>
                            <div
                                className={`flex gap-3 items-start ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                                    }`}
                            >
                                <div className="flex-shrink-0">
                                    {msg.role === 'user' ? (
                                        <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
                                            J
                                        </div>
                                    ) : (
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-2xl">
                                            🤖
                                        </div>
                                    )}
                                </div>

                                <div className={`max-w-[70%] ${msg.role === 'user' ? '' : 'w-full'}`}>
                                    <div
                                        className={`rounded-2xl px-5 py-4 shadow-sm ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-white text-gray-900 border border-gray-100'
                                            }`}
                                    >
                                        {msg.role === 'user' ? (
                                            <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                                        ) : (
                                            <div className="prose prose-sm max-w-none prose-headings:mt-3 prose-headings:mb-2 prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-1">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {msg.content}
                                                </ReactMarkdown>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}

                    {isStreaming && (
                        <div className="flex justify-start">
                            <div className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 shadow-sm border border-gray-100">
                                <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                                <span className="text-sm text-gray-600">AI正在思考中...</span>
                            </div>
                        </div>
                    )}

                    {/* Workflow Progress Display */}
                    {workflowState.isActive && (
                        <div className="mb-4">
                            <WorkflowProgress
                                workflowName={workflowState.workflowName || '工作流执行中'}
                                steps={workflowState.steps}
                                currentStepIndex={workflowState.currentStepIndex}
                                totalSteps={workflowState.totalSteps}
                                elapsedMs={workflowState.elapsedMs}
                                isCompleted={workflowState.isCompleted}
                                isFailed={workflowState.isFailed}
                            />
                        </div>
                    )}

                    {/* 🆕 Orchestrator Workflow Progress Display */}
                    {orchestratorRunning && orchestratorSteps.length > 0 && (
                        <div className="mb-4">
                            <WorkflowProgress
                                workflowName="简历优化工作流"
                                steps={orchestratorSteps}
                                currentStepIndex={orchestratorSteps.findIndex(s => s.status === 'running')}
                                totalSteps={orchestratorSteps.length}
                                elapsedMs={0}
                                isCompleted={false}
                                isFailed={false}
                            />
                        </div>
                    )}

                    {/* 🆕 Orchestrator Result Display */}
                    {orchestratorResult && (
                        <div className="mb-4">
                            <WorkflowResult
                                result={orchestratorResult}
                                isLoading={false}
                                onRetry={() => {
                                    // 可选：重新执行工作流
                                    const documentIds = uploadedFiles.map(f => f.document_id)
                                    if (messages.length > 0) {
                                        const lastUserMsg = [...messages].reverse().find(m => m.role === 'user')
                                        if (lastUserMsg) {
                                            handleOrchestratorChat(lastUserMsg.content, documentIds)
                                        }
                                    }
                                }}
                            />
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="border-t bg-white p-4 shadow-lg flex-shrink-0">
                <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
                    {/* 已上传文件列表 */}
                    {uploadedFiles.length > 0 && (
                        <div className="mb-3 flex flex-wrap gap-2">
                            {uploadedFiles.map((file, index) => (
                                <div
                                    key={index}
                                    className="flex items-center gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg text-sm"
                                >
                                    <FileText className="h-4 w-4 text-blue-600" />
                                    <span className="text-blue-900 font-medium">{file.file_name}</span>
                                    <span className="text-blue-600 text-xs">
                                        ({(file.file_size / 1024).toFixed(1)}KB)
                                    </span>
                                    <button
                                        type="button"
                                        onClick={() => handleRemoveFile(index)}
                                        className="ml-1 p-0.5 hover:bg-blue-200 rounded transition-colors"
                                        title="移除文件"
                                    >
                                        <X className="h-3 w-3 text-blue-700" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* 上传进度条 */}
                    {uploading && (
                        <div className="mb-3 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg">
                            <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                                <span>上传中...</span>
                                <span>{uploadProgress}%</span>
                            </div>
                            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-600 transition-all duration-300"
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {/* 隐藏的文件输入 */}
                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        onChange={handleFileSelect}
                    />

                    <div className="relative flex items-end gap-3 bg-gray-50 p-2 rounded-xl border border-gray-200 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
                        {/* 文件上传按钮组 */}
                        <div className="flex gap-1">
                            <button
                                type="button"
                                onClick={() => handleUploadClick('image')}
                                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="上传图片 (JPG, PNG, GIF)"
                                disabled={uploading}
                            >
                                <ImageIcon className="h-5 w-5" />
                            </button>
                            <button
                                type="button"
                                onClick={() => handleUploadClick('video')}
                                className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                                title="上传视频 (MP4, MOV)"
                                disabled={uploading}
                            >
                                <Video className="h-5 w-5" />
                            </button>
                            <button
                                type="button"
                                onClick={() => handleUploadClick('document')}
                                className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                title="上传文档 (PDF, Word, TXT, CSV)"
                                disabled={uploading}
                            >
                                <Paperclip className="h-5 w-5" />
                            </button>
                        </div>

                        <textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    handleSubmit(e)
                                }
                            }}
                            placeholder={`问${aiFunction.name}任何问题... (Enter发送，Shift+Enter换行)`}
                            disabled={isStreaming}
                            className="flex-1 max-h-32 min-h-[44px] bg-transparent border-0 focus:ring-0 resize-none py-3 text-sm text-gray-900 placeholder:text-gray-400 disabled:opacity-50"
                            rows={1}
                            autoFocus
                        />

                        <button
                            type="submit"
                            disabled={!inputValue.trim() || isStreaming}
                            className="p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors mb-0.5"
                        >
                            {isStreaming ? (
                                <Loader2 className="h-5 w-5 animate-spin" />
                            ) : (
                                <Send className="h-5 w-5" />
                            )}
                        </button>
                    </div>
                    <p className="text-center text-xs text-gray-400 mt-2">
                        AI生成内容仅供参考，请核实重要信息
                    </p>
                </form>
            </div>
        </div>
    )
}

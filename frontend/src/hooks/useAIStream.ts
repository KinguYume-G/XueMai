import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { API_BASE_URL } from '@/lib/api/client'
import { getAccessToken } from '@/lib/auth/token'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface UseAIStreamReturn {
  messages: Message[]
  isStreaming: boolean
  error: string | null
  sendMessage: (text: string, useRag?: boolean) => Promise<void>
  clearMessages: () => void
}

export function useAIStream(): UseAIStreamReturn {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const navigate = useNavigate()

  const sendMessage = useCallback(async (text: string, useRag: boolean = true) => {
    if (!text.trim() || isStreaming) return

    // 清除之前的错误
    setError(null)

    // 添加用户消息
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])

    // 创建空的AI消息
    const assistantMessageId = `assistant-${Date.now()}`
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, assistantMessage])

    // 开始流式传输
    setIsStreaming(true)

    // 创建AbortController用于取消请求
    abortControllerRef.current = new AbortController()

    try {
      // 获取token
      const token = getAccessToken()
      if (!token) {
        navigate('/login')
        return
      }

      // 发送请求
      const response = await fetch(`${API_BASE_URL}/ai/chat/stream/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          question: text.trim(),
          use_rag: useRag,
        }),
        signal: abortControllerRef.current.signal,
      })

      // 检查响应状态
      if (response.status === 401) {
        navigate('/login')
        return
      }

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`)
      }

      // 读取流式响应
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法获取响应流')
      }

      const decoder = new TextDecoder()
      let accumulatedText = ''
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        // 解码chunk
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim() || !line.startsWith('data: ')) continue

          const data = line.slice(6) // 移除 "data: "

          if (data === '[DONE]') {
            // 流式传输完成
            continue
          }

          try {
            const parsed = JSON.parse(data)

            if (parsed.type === 'text') {
              // 累积文本
              accumulatedText += parsed.content

              // 更新AI消息
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: accumulatedText }
                    : msg
                )
              )
            } else if (parsed.type === 'error') {
              // 错误消息
              setError(parsed.message || '生成回答时出错')
            } else if (parsed.type === 'done') {
              // 完成，可以记录耗时
              continue
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e, data)
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('请求被取消')
      } else {
        console.error('流式请求失败:', err)
        setError(err.message || '网络连接失败，请重试')
      }
    } finally {
      setIsStreaming(false)
      abortControllerRef.current = null
    }
  }, [isStreaming, navigate])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isStreaming,
    error,
    sendMessage,
    clearMessages,
  }
}

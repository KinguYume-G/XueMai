import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { WorkflowStep } from '@/components/ai/WorkflowProgress'
import {
  extractConversationId,
  getSseData,
  splitSseFrames,
} from '@/lib/api/contracts'
import { apiFetch, readApiErrorMessage } from '@/lib/api/client'
import { getAccessToken } from '@/lib/auth/token'
import { toast } from '@/store/useToastStore'

interface MessageMetadata {
  routed_to?: string
  confidence?: number
  method?: string
  elapsed_ms?: number
  chunks?: number
  used_rag?: boolean
  model?: string
  context_messages_count?: number
  total_tokens?: number
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  metadata?: MessageMetadata
}

interface AIStreamConfig {
  mode?: string
  systemPrompt?: string
  useRag?: boolean
  conversationId?: number
}

interface WorkflowState {
  isActive: boolean
  workflowId?: string
  workflowName?: string
  steps: WorkflowStep[]
  currentStepIndex: number
  totalSteps: number
  elapsedMs?: number
  isCompleted: boolean
  isFailed: boolean
  error?: string
}

interface UseAIStreamReturn {
  messages: Message[]
  isStreaming: boolean
  error: string | null
  sendMessage: (text: string, useRag?: boolean, documentIds?: number[]) => Promise<void>
  clearMessages: () => void
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
  conversationId?: number
  workflowState: WorkflowState
}

type StreamEvent = Record<string, unknown> & { type?: string }

const initialWorkflowState = (): WorkflowState => ({
  isActive: false,
  steps: [],
  currentStepIndex: 0,
  totalSteps: 0,
  isCompleted: false,
  isFailed: false,
})

const asString = (value: unknown): string | undefined =>
  typeof value === 'string' ? value : undefined

const asNumber = (value: unknown): number | undefined =>
  typeof value === 'number' && Number.isFinite(value) ? value : undefined

export function useAIStream(config?: AIStreamConfig): UseAIStreamReturn {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<number | undefined>(
    config?.conversationId,
  )
  const [workflowState, setWorkflowState] = useState<WorkflowState>(
    initialWorkflowState,
  )
  const abortControllerRef = useRef<AbortController | null>(null)
  const conversationIdRef = useRef<number | undefined>(config?.conversationId)
  const navigate = useNavigate()

  useEffect(() => {
    conversationIdRef.current = config?.conversationId
    setConversationId(config?.conversationId)
  }, [config?.conversationId])

  useEffect(
    () => () => {
      abortControllerRef.current?.abort()
    },
    [],
  )

  const clearMessages = useCallback(() => {
    abortControllerRef.current?.abort()
    setMessages([])
    setError(null)
    setWorkflowState(initialWorkflowState())
  }, [])

  const updateConversationId = useCallback((event: StreamEvent) => {
    const nextId = extractConversationId(event)
    if (nextId && nextId !== conversationIdRef.current) {
      conversationIdRef.current = nextId
      setConversationId(nextId)
    }
  }, [])

  const sendMessage = useCallback(async (
    text: string,
    useRag: boolean = config?.useRag ?? true,
    documentIds: number[] = [],
  ) => {
    const question = text.trim()
    if (!question || isStreaming) return

    setError(null)
    setWorkflowState(initialWorkflowState())

    const requestStartedAt = Date.now()
    const userMessage: Message = {
      id: `user-${requestStartedAt}`,
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    const assistantMessageId = `assistant-${requestStartedAt}`
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    }

    setMessages((previous) => [...previous, userMessage, assistantMessage])
    setIsStreaming(true)

    const abortController = new AbortController()
    abortControllerRef.current = abortController
    let accumulatedText = ''
    const metadata: MessageMetadata = {}

    const updateAssistantMessage = () => {
      setMessages((previous) =>
        previous.map((message) =>
          message.id === assistantMessageId
            ? { ...message, content: accumulatedText, metadata: { ...metadata } }
            : message,
        ),
      )
    }

    const removeEmptyAssistantMessage = () => {
      if (accumulatedText) return
      setMessages((previous) =>
        previous.filter((message) => message.id !== assistantMessageId),
      )
    }

    const handleEvent = (event: StreamEvent) => {
      updateConversationId(event)

      switch (event.type) {
        case 'metadata':
          metadata.routed_to = asString(event.routed_to)
          metadata.confidence = asNumber(event.confidence)
          metadata.method = asString(event.method)
          metadata.used_rag = useRag
          break

        case 'text':
          accumulatedText += asString(event.content) ?? ''
          break

        case 'done':
          metadata.elapsed_ms = asNumber(event.elapsed_ms)
          metadata.chunks = asNumber(event.chunks)
          break

        case 'workflow_start':
          setWorkflowState((previous) => ({
            ...previous,
            isActive: true,
            workflowId: asString(event.workflow_id),
            workflowName: asString(event.workflow_name),
            totalSteps: asNumber(event.total_steps) ?? 0,
            steps: [],
            isCompleted: false,
            isFailed: false,
          }))
          break

        case 'workflow_completed':
          setWorkflowState((previous) => ({
            ...previous,
            isCompleted: true,
            elapsedMs: asNumber(event.elapsed_ms),
          }))
          break

        case 'workflow_failed': {
          const workflowError = asString(event.error) ?? '工作流执行失败'
          setWorkflowState((previous) => ({
            ...previous,
            isFailed: true,
            error: workflowError,
          }))
          setError(workflowError)
          break
        }

        case 'step_start': {
          const stepId = asString(event.step_id) ?? `step-${Date.now()}`
          setWorkflowState((previous) => {
            if (previous.steps.some((step) => step.id === stepId)) return previous
            return {
              ...previous,
              steps: [
                ...previous.steps,
                {
                  id: stepId,
                  name: asString(event.step_name) ?? '处理中',
                  description: asString(event.description) ?? '',
                  status: 'running',
                },
              ],
            }
          })
          break
        }

        case 'step_completed': {
          const stepId = asString(event.step_id) ?? `step-${Date.now()}`
          setWorkflowState((previous) => {
            const completedStep: WorkflowStep = {
              id: stepId,
              name: asString(event.step_name) ?? '已完成',
              description: '',
              status: 'completed',
              result: typeof event.result === 'string'
                ? event.result
                : event.result == null
                  ? undefined
                  : JSON.stringify(event.result),
            }
            const index = previous.steps.findIndex((step) => step.id === stepId)
            const steps = [...previous.steps]
            if (index >= 0) steps[index] = completedStep
            else steps.push(completedStep)
            return {
              ...previous,
              steps,
              currentStepIndex: asNumber(event.completed) ?? previous.currentStepIndex,
            }
          })
          break
        }

        case 'step_failed': {
          const stepId = asString(event.step_id) ?? `step-${Date.now()}`
          const stepError = asString(event.error) ?? '步骤执行失败'
          setWorkflowState((previous) => {
            const failedStep: WorkflowStep = {
              id: stepId,
              name: asString(event.step_name) ?? '执行失败',
              description: '',
              status: 'failed',
              error: stepError,
            }
            const index = previous.steps.findIndex((step) => step.id === stepId)
            const steps = [...previous.steps]
            if (index >= 0) steps[index] = { ...steps[index], ...failedStep }
            else steps.push(failedStep)
            return { ...previous, steps }
          })
          break
        }

        case 'final_result': {
          const results = event.results
          if (results && typeof results === 'object' && 'answer' in results) {
            accumulatedText += asString((results as { answer?: unknown }).answer) ?? ''
          }
          break
        }

        case 'error': {
          const streamError = asString(event.message) ?? '生成回答时出错'
          setError(streamError)
          toast.error(streamError)
          break
        }
      }

      updateAssistantMessage()
    }

    const handleFrame = (frame: string) => {
      const data = getSseData(frame)
      if (!data || data === '[DONE]') return

      try {
        handleEvent(JSON.parse(data) as StreamEvent)
      } catch (parseError) {
        console.error('解析 AI 流事件失败:', parseError)
      }
    }

    try {
      if (!getAccessToken()) {
        navigate('/login')
        return
      }

      const response = await apiFetch('/ai/chat/stream/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          mode: config?.mode,
          system_prompt: config?.systemPrompt,
          use_rag: useRag,
          conversation_id: conversationIdRef.current ?? null,
          document_ids: documentIds,
        }),
        signal: abortController.signal,
      })

      if (!response.ok) {
        const message = await readApiErrorMessage(response)
        if (response.status === 401) navigate('/login')
        throw new Error(message)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('无法读取 AI 响应流')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const split = splitSseFrames(buffer)
        buffer = split.remainder
        split.frames.forEach(handleFrame)
      }

      buffer += decoder.decode()
      splitSseFrames(buffer, true).frames.forEach(handleFrame)
    } catch (streamError: unknown) {
      if (streamError instanceof DOMException && streamError.name === 'AbortError') {
        return
      }

      const message = streamError instanceof Error
        ? streamError.message
        : '网络连接失败，请重试'
      setError(message)
      toast.error(message)
    } finally {
      removeEmptyAssistantMessage()
      setIsStreaming(false)
      if (abortControllerRef.current === abortController) {
        abortControllerRef.current = null
      }
    }
  }, [
    config?.mode,
    config?.systemPrompt,
    config?.useRag,
    isStreaming,
    navigate,
    updateConversationId,
  ])

  return {
    messages,
    isStreaming,
    error,
    sendMessage,
    clearMessages,
    setMessages,
    conversationId,
    workflowState,
  }
}

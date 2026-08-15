import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send } from 'lucide-react'

interface AIChatInputProps {
  onSend?: (message: string) => void
  disabled?: boolean
}

/**
 * AI 聊天输入框组件
 * 底部固定的聊天输入区域，包含输入框、附件按钮和发送按钮
 */
export default function AIChatInput({ onSend, disabled = false }: AIChatInputProps) {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (message.trim()) {
      if (onSend) {
        onSend(message)
      }
      setMessage('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Card className="sticky bottom-0 left-0 right-0 bg-white border-t shadow-lg rounded-none">
      <div className="p-4">
        <div className="flex items-end gap-3">
          {/* 输入框 */}
          <div className="flex-1">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="选择功能开始对话，或直接输入您的问题..."
              className="h-10 resize-none border-2 focus:border-primary"
              disabled={disabled}
            />
          </div>

          {/* 发送按钮 */}
          <Button
            onClick={handleSend}
            disabled={!message.trim() || disabled}
            className="h-10 w-10 rounded-full p-0"
            size="icon"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>

        {/* 提示文字 */}
        <div className="mt-2 text-xs text-muted-foreground text-center">
          学脉AI助手由先进的人工智能驱动，可能会生成不准确的信息
        </div>
      </div>
    </Card>
  )
}

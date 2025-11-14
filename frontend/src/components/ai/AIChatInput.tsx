import { useState, useRef } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, Video, Image as ImageIcon, FileText } from 'lucide-react'

interface AIChatInputProps {
  onSend?: (message: string) => void
}

/**
 * AI 聊天输入框组件
 * 底部固定的聊天输入区域，包含输入框、附件按钮和发送按钮
 */
export default function AIChatInput({ onSend }: AIChatInputProps) {
  const [message, setMessage] = useState('')
  const videoInputRef = useRef<HTMLInputElement>(null)
  const imageInputRef = useRef<HTMLInputElement>(null)
  const documentInputRef = useRef<HTMLInputElement>(null)

  const handleSend = () => {
    if (message.trim()) {
      console.log('发送消息:', message)
      if (onSend) {
        onSend(message)
      }
      // 显示提示
      alert('AI助手功能正在开发中，敬请期待！\n您的消息：' + message)
      setMessage('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileUpload = (type: 'video' | 'image' | 'document') => {
    console.log('上传附件类型:', type)
    alert(`${type === 'video' ? '视频' : type === 'image' ? '图片' : '文档'}上传功能正在开发中！`)
  }

  return (
    <Card className="sticky bottom-0 left-0 right-0 bg-white border-t shadow-lg rounded-none">
      <div className="p-4">
        <div className="flex items-end gap-3">
          {/* 附件按钮组 */}
          <div className="flex gap-2">
            {/* 视频上传 */}
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 rounded-full"
              onClick={() => handleFileUpload('video')}
              title="上传视频"
            >
              <Video className="h-5 w-5" />
            </Button>

            {/* 图片上传 */}
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 rounded-full"
              onClick={() => handleFileUpload('image')}
              title="上传图片"
            >
              <ImageIcon className="h-5 w-5" />
            </Button>

            {/* 文档上传 */}
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 rounded-full"
              onClick={() => handleFileUpload('document')}
              title="上传文档"
            >
              <FileText className="h-5 w-5" />
            </Button>

            {/* 隐藏的文件输入框 */}
            <input
              ref={videoInputRef}
              type="file"
              accept="video/*"
              className="hidden"
            />
            <input
              ref={imageInputRef}
              type="file"
              accept="image/*"
              className="hidden"
            />
            <input
              ref={documentInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              className="hidden"
            />
          </div>

          {/* 输入框 */}
          <div className="flex-1">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="选择功能开始对话，或直接输入您的问题..."
              className="h-10 resize-none border-2 focus:border-primary"
            />
          </div>

          {/* 发送按钮 */}
          <Button
            onClick={handleSend}
            disabled={!message.trim()}
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

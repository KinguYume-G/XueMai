import { useEffect } from 'react'
import { Headphones, X, Send, Mic } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { useChatWidgetStore } from '@/store/useChatWidgetStore'

export default function ChatWidget() {
  const { isOpen, toggle, close } = useChatWidgetStore()

  // ESC键关闭聊天窗
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        close()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, close])

  const handleSendMessage = () => {
    console.log('Send message clicked')
  }

  const handleMicClick = () => {
    console.log('Mic clicked')
  }

  return (
    <>
      {/* Talk with Us 按钮 */}
      <Button
        onClick={toggle}
        className="fixed bottom-6 right-6 bg-black text-white rounded-full px-4 h-11 shadow-lg flex items-center gap-2 hover:bg-gray-800 transition-colors z-50 md:bottom-6 md:right-6 max-md:bottom-4 max-md:right-4 max-md:scale-95"
        aria-label="Talk with Us"
      >
        <Headphones className="h-6 w-6" />
        <span className="font-medium">Talk with Us</span>
      </Button>

      {/* 聊天窗口 */}
      {isOpen && (
        <Card className="fixed bottom-20 right-6 w-[380px] h-[520px] bg-white rounded-2xl shadow-2xl border z-50 overflow-hidden animate-in slide-in-from-bottom-4 md:bottom-20 md:right-6 md:w-[380px] md:h-[520px] max-md:bottom-16 max-md:right-4 max-md:w-[92vw] max-md:h-[70vh]">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b bg-gray-50">
            <h3 className="font-semibold text-gray-900">Talk with Us</h3>
            <Button
              variant="ghost"
              size="icon"
              onClick={close}
              className="h-8 w-8 rounded-full hover:bg-gray-200"
              aria-label="Close chat"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Body - 滚动区域 */}
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="flex items-center justify-center h-full text-gray-500 text-center">
              <div>
                <Headphones className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm">Use voice or text to communicate</p>
              </div>
            </div>
          </div>

          {/* Footer - 输入区域 */}
          <div className="p-4 border-t bg-gray-50">
            <div className="flex items-center gap-2">
              <Input
                placeholder="Type your message..."
                className="flex-1 rounded-full border-gray-300 focus:border-black focus:ring-black"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSendMessage()
                  }
                }}
              />
              <Button
                size="icon"
                onClick={handleSendMessage}
                className="rounded-full bg-black hover:bg-gray-800 text-white"
                aria-label="Send message"
              >
                <Send className="h-4 w-4" />
              </Button>
              <Button
                size="icon"
                variant="outline"
                onClick={handleMicClick}
                className="rounded-full border-gray-300 hover:bg-gray-100"
                aria-label="Voice message"
              >
                <Mic className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      )}
    </>
  )
}

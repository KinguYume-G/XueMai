import { useState } from 'react'
import { Card } from '@/components/ui/card'
import AICategoryNav from '@/components/ai/AICategoryNav'
import AIFunctionCard from '@/components/ai/AIFunctionCard'
import AIChatInput from '@/components/ai/AIChatInput'
import AIWelcome from '@/components/ai/AIWelcome'
import type { AICategoryId } from '@/types/ai'
import { aiCategories } from '@/types/ai'
import { useAIStream } from '@/hooks/useAIStream'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * 学脉AI助手主页面
 * 包含左侧导航、中间内容区和底部聊天输入框
 */
export default function AIAssistant() {
  const [activeCategory, setActiveCategory] = useState<AICategoryId | null>(null)
  const { messages, isStreaming, error, sendMessage } = useAIStream()

  // 获取当前选中分类的数据
  const currentCategory = activeCategory
    ? aiCategories.find((cat) => cat.id === activeCategory)
    : null

  // 处理子功能卡片点击
  const handleFunctionClick = (functionId: string) => {
    const feature = currentCategory?.functions.find((item) => item.id === functionId)
    if (feature) sendMessage(`请作为${feature.name}助手帮助我。请先告诉我需要提供哪些信息。`)
  }

  // 处理发送消息
  const handleSendMessage = (message: string) => {
    sendMessage(message)
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)] relative">
      {/* 左侧导航栏 */}
      <aside className="w-72 flex-shrink-0 overflow-y-auto">
        <AICategoryNav
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
        />
      </aside>

      {/* 中间主内容区 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto pb-6">
          <Card className="min-h-full rounded-xl border shadow-sm p-6">
            {messages.length > 0 ? (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                      {message.role === 'assistant' ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content || '正在生成…'}</ReactMarkdown> : message.content}
                    </div>
                  </div>
                ))}
                {error && <p className="text-sm text-destructive">{error}</p>}
              </div>
            ) : !currentCategory ? (
              // 未选择分类时显示欢迎界面
              <AIWelcome />
            ) : (
              // 选择分类后显示该分类的子功能
              <div className="space-y-6">
                {/* 分类标题 */}
                <div className="flex items-center gap-3 pb-4 border-b">
                  <span className="text-4xl">{currentCategory.icon}</span>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">
                      {currentCategory.name}
                    </h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      选择下方功能开始使用
                    </p>
                  </div>
                </div>

                {/* 子功能卡片网格 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentCategory.functions.map((func) => (
                    <AIFunctionCard
                      key={func.id}
                      function={func}
                      onClick={handleFunctionClick}
                    />
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>

        {/* 底部聊天输入框 */}
        <div className="flex-shrink-0 mt-4">
          <AIChatInput onSend={handleSendMessage} disabled={isStreaming} />
        </div>
      </main>
    </div>
  )
}

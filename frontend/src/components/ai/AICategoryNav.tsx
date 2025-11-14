import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageSquare } from 'lucide-react'
import type { AICategoryId } from '@/types/ai'
import { aiCategories, mockConversationHistory } from '@/types/ai'

interface AICategoryNavProps {
  activeCategory: AICategoryId | null
  onCategoryChange: (categoryId: AICategoryId) => void
}

/**
 * AI 分类导航组件
 * 显示左侧的5个AI功能分类和对话历史
 */
export default function AICategoryNav({ activeCategory, onCategoryChange }: AICategoryNavProps) {
  return (
    <div className="space-y-4">
      {/* AI 功能分类 */}
      <Card className="rounded-xl border shadow-sm">
        <CardHeader className="pb-3 px-4 pt-4">
          <CardTitle className="text-base font-semibold">AI 功能分类</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 px-2 pb-2">
          {aiCategories.map((category) => (
            <Button
              key={category.id}
              variant={activeCategory === category.id ? 'secondary' : 'ghost'}
              className={`w-full justify-start gap-3 h-11 px-4 ${
                activeCategory === category.id ? 'bg-secondary font-medium' : ''
              }`}
              onClick={() => onCategoryChange(category.id)}
            >
              <span className="text-xl">{category.icon}</span>
              <span>{category.name}</span>
            </Button>
          ))}
        </CardContent>
      </Card>

      {/* 对话历史 */}
      <Card className="rounded-xl border shadow-sm">
        <CardHeader className="pb-3 px-4 pt-4">
          <CardTitle className="flex items-center gap-2 text-base font-semibold">
            <MessageSquare className="h-5 w-5 text-primary" />
            对话历史
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 px-2 pb-2">
          {mockConversationHistory.map((conversation) => (
            <button
              key={conversation.id}
              className="flex w-full flex-col items-start rounded-lg px-3 py-3 text-sm transition-colors hover:bg-secondary/80 cursor-pointer"
              onClick={() => {
                console.log('打开对话:', conversation.title)
              }}
            >
              <span className="font-medium text-foreground line-clamp-1">
                {conversation.title}
              </span>
              <span className="text-xs text-muted-foreground">
                {conversation.timestamp}
              </span>
            </button>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

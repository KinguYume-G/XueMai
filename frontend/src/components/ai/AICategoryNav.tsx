import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import type { AICategoryId } from '@/types/ai'
import { aiCategories } from '@/types/ai'

interface AICategoryNavProps {
  activeCategory: AICategoryId | null
  onCategoryChange: (categoryId: AICategoryId) => void
}

/**
 * AI 分类导航组件
 * 显示左侧的5个AI功能分类
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
    </div>
  )
}

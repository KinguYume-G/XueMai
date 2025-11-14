import { Card, CardContent } from '@/components/ui/card'
import type { AIFunction } from '@/types/ai'

interface AIFunctionCardProps {
  function: AIFunction
  onClick: (functionId: string) => void
}

/**
 * AI 功能卡片组件
 * 展示单个 AI 子功能，包含图标、名称和描述
 */
export default function AIFunctionCard({ function: func, onClick }: AIFunctionCardProps) {
  return (
    <Card
      className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-primary/50 group"
      onClick={() => onClick(func.id)}
    >
      <CardContent className="p-6">
        <div className="flex flex-col items-center text-center space-y-3">
          {/* 图标 */}
          <div className="text-4xl group-hover:scale-110 transition-transform duration-200">
            {func.icon}
          </div>

          {/* 功能名称 */}
          <h3 className="font-semibold text-base text-foreground group-hover:text-primary transition-colors">
            {func.name}
          </h3>

          {/* 功能描述 */}
          <p className="text-sm text-muted-foreground line-clamp-2">
            {func.description}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

import { Bot, Sparkles, MessageCircle, Zap } from 'lucide-react'

/**
 * AI 助手欢迎界面组件
 * 在用户未选择任何分类时显示
 */
export default function AIWelcome() {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6">
      {/* 主图标 */}
      <div className="relative mb-8">
        <div className="absolute inset-0 bg-primary/20 rounded-full blur-3xl animate-pulse" />
        <div className="relative bg-gradient-to-br from-primary to-purple-600 rounded-full p-6">
          <Bot className="h-16 w-16 text-white" />
        </div>
      </div>

      {/* 欢迎标题 */}
      <h1 className="text-3xl font-bold text-foreground mb-4 flex items-center gap-2">
        欢迎使用学脉AI助手
        <Sparkles className="h-6 w-6 text-yellow-500" />
      </h1>

      {/* 欢迎描述 */}
      <p className="text-lg text-muted-foreground text-center max-w-2xl mb-12">
        您的智能学习与职业发展伙伴，提供全方位的AI辅助服务
      </p>

      {/* 功能特色 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl w-full">
        <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100/50 border border-blue-200">
          <div className="bg-blue-500 rounded-full p-3 mb-4">
            <MessageCircle className="h-6 w-6 text-white" />
          </div>
          <h3 className="font-semibold text-foreground mb-2">智能对话</h3>
          <p className="text-sm text-muted-foreground">
            自然流畅的AI对话体验，理解您的需求
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gradient-to-br from-purple-50 to-purple-100/50 border border-purple-200">
          <div className="bg-purple-500 rounded-full p-3 mb-4">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <h3 className="font-semibold text-foreground mb-2">专业建议</h3>
          <p className="text-sm text-muted-foreground">
            基于大数据的专业学业和职业建议
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gradient-to-br from-green-50 to-green-100/50 border border-green-200">
          <div className="bg-green-500 rounded-full p-3 mb-4">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <h3 className="font-semibold text-foreground mb-2">高效助手</h3>
          <p className="text-sm text-muted-foreground">
            快速响应，提升您的学习和工作效率
          </p>
        </div>
      </div>

      {/* 提示文字 */}
      <div className="mt-12 text-center">
        <p className="text-sm text-muted-foreground">
          从左侧选择功能分类开始使用，或在下方直接输入您的问题
        </p>
      </div>
    </div>
  )
}

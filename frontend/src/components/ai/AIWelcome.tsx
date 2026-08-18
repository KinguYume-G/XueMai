import { Bot, Sparkles, MessageCircle, Zap } from 'lucide-react'
import { useTranslation } from 'react-i18next'

/**
 * AI 助手欢迎界面组件
 * 在用户未选择任何分类时显示
 */
export default function AIWelcome() {
  const { t } = useTranslation()
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
        {t('aiChat.welcome.title')}
        <Sparkles className="h-6 w-6 text-yellow-500" />
      </h1>

      {/* 欢迎描述 */}
      <p className="text-lg text-muted-foreground text-center max-w-2xl mb-12">
        {t('aiChat.welcome.subtitle')}
      </p>

      {/* 功能特色 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl w-full">
        <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100/50 border border-blue-200">
          <div className="bg-blue-500 rounded-full p-3 mb-4">
            <MessageCircle className="h-6 w-6 text-white" />
          </div>
          <h3 className="font-semibold text-foreground mb-2">{t('aiChat.welcome.chat.title')}</h3>
          <p className="text-sm text-muted-foreground">
            {t('aiChat.welcome.chat.description')}
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gradient-to-br from-purple-50 to-purple-100/50 border border-purple-200">
          <div className="bg-purple-500 rounded-full p-3 mb-4">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <h3 className="font-semibold text-foreground mb-2">{t('aiChat.welcome.advice.title')}</h3>
          <p className="text-sm text-muted-foreground">
            {t('aiChat.welcome.advice.description')}
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gradient-to-br from-green-50 to-green-100/50 border border-green-200">
          <div className="bg-green-500 rounded-full p-3 mb-4">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <h3 className="font-semibold text-foreground mb-2">{t('aiChat.welcome.efficient.title')}</h3>
          <p className="text-sm text-muted-foreground">
            {t('aiChat.welcome.efficient.description')}
          </p>
        </div>
      </div>

      {/* 提示文字 */}
      <div className="mt-12 text-center">
        <p className="text-sm text-muted-foreground">
          {t('aiChat.welcome.hint')}
        </p>
      </div>
    </div>
  )
}

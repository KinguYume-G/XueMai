import { useCallback, useEffect, useMemo } from 'react'
import { Minus, HelpCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { useChatWidgetStore } from '@/store/useChatWidgetStore'

const CHAT_WIDGET_PANEL_ID = 'chat-widget-panel'
const CHAT_WIDGET_TITLE_ID = 'chat-widget-title'

export default function ChatWidget() {
  const isOpen = useChatWidgetStore((state) => state.isOpen)
  const openWidget = useChatWidgetStore((state) => state.open)
  const closeWidget = useChatWidgetStore((state) => state.close)
  const toggleWidget = useChatWidgetStore((state) => state.toggle)

  useEffect(() => {
    if (!isOpen) {
      return
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeWidget()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, closeWidget])

  const handleOpenChange = useCallback(
    (next: boolean) => {
      if (next) {
        openWidget()
      } else {
        closeWidget()
      }
    },
    [openWidget, closeWidget]
  )

  const buttonSafeAreaStyle = useMemo(
    () => ({
      bottom: 'calc(env(safe-area-inset-bottom, 0px) + 1.5rem)',
      right: 'calc(env(safe-area-inset-right, 0px) + 1.5rem)',
    }),
    []
  )

  const panelSafeAreaStyle = useMemo(
    () => ({
      marginBottom: 'calc(env(safe-area-inset-bottom, 0px) + 6rem)',
      marginRight: 'calc(env(safe-area-inset-right, 0px) + 1.5rem)',
    }),
    []
  )

  return (
    <>
      <Button
        type="button"
        onClick={toggleWidget}
        aria-label="Open help center"
        aria-expanded={isOpen}
        aria-controls={CHAT_WIDGET_PANEL_ID}
        className="fixed z-[110] flex items-center gap-2 rounded-full bg-black px-5 py-3 text-sm font-medium text-white shadow-lg transition-all hover:shadow-xl focus-visible:ring-2 focus-visible:ring-white/60 focus-visible:ring-offset-2 focus-visible:ring-offset-black active:scale-[0.98]"
        style={buttonSafeAreaStyle}
      >
        <HelpCircle className="h-5 w-5" />
        <span className="text-sm font-semibold">帮助与支持</span>
      </Button>

      <Dialog open={isOpen} onOpenChange={handleOpenChange}>
        <DialogContent
          id={CHAT_WIDGET_PANEL_ID}
          aria-labelledby={CHAT_WIDGET_TITLE_ID}
          containerClassName="p-0"
          className="w-[min(380px,calc(100vw-3rem))] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
          style={panelSafeAreaStyle}
        >
          <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
            <div className="flex items-center gap-3">
              <HelpCircle className="h-6 w-6 text-slate-700" />
              <div>
                <p id={CHAT_WIDGET_TITLE_ID} className="text-sm font-semibold text-slate-900">
                  帮助与支持
                </p>
                <p className="text-xs text-slate-500">
                  选择您需要的服务
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                aria-label="Close help center"
                onClick={closeWidget}
                className="rounded-full p-1 text-slate-500 transition-colors hover:bg-slate-200 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400"
              >
                <Minus className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="flex flex-col bg-white p-6">
            <div className="grid grid-cols-2 gap-3">
              {/* 卡片1: AI助手 */}
              <button
                onClick={() => window.location.href = '/ai'}
                className="flex flex-col items-start gap-2 rounded-xl bg-blue-50 p-4 text-left transition-all hover:bg-blue-100 hover:shadow-md active:scale-[0.98]"
              >
                <span className="text-2xl">🤖</span>
                <div>
                  <p className="font-semibold text-slate-900">AI助手</p>
                  <p className="text-xs text-slate-600">智能学业辅导</p>
                </div>
              </button>

              {/* 卡片2: 在线客服 */}
              <button
                onClick={() => alert('客服功能即将开放，敬请期待！')}
                className="flex flex-col items-start gap-2 rounded-xl bg-green-50 p-4 text-left transition-all hover:bg-green-100 hover:shadow-md active:scale-[0.98] opacity-75"
              >
                <span className="text-2xl">💬</span>
                <div>
                  <p className="font-semibold text-slate-900">在线客服</p>
                  <p className="text-xs text-slate-600">即将开放</p>
                </div>
              </button>

              {/* 卡片3: 帮助文档 */}
              <button
                onClick={() => alert('帮助文档正在建设中')}
                className="flex flex-col items-start gap-2 rounded-xl bg-purple-50 p-4 text-left transition-all hover:bg-purple-100 hover:shadow-md active:scale-[0.98]"
              >
                <span className="text-2xl">📚</span>
                <div>
                  <p className="font-semibold text-slate-900">帮助文档</p>
                  <p className="text-xs text-slate-600">常见问题</p>
                </div>
              </button>

              {/* 卡片4: 反馈建议 */}
              <button
                onClick={() => alert('请发送邮件至\nfeedback@unipulse.asia')}
                className="flex flex-col items-start gap-2 rounded-xl bg-orange-50 p-4 text-left transition-all hover:bg-orange-100 hover:shadow-md active:scale-[0.98]"
              >
                <span className="text-2xl">💡</span>
                <div>
                  <p className="font-semibold text-slate-900">反馈建议</p>
                  <p className="text-xs text-slate-600">帮助改进</p>
                </div>
              </button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
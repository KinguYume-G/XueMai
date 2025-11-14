import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Headphones, Mic, Minus, Send, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { useChatWidgetStore } from '@/store/useChatWidgetStore'
import { cn } from '@/lib/utils'

const CHAT_WIDGET_PANEL_ID = 'chat-widget-panel'
const CHAT_WIDGET_TITLE_ID = 'chat-widget-title'

export default function ChatWidget() {
  const isOpen = useChatWidgetStore((state) => state.isOpen)
  const openWidget = useChatWidgetStore((state) => state.open)
  const closeWidget = useChatWidgetStore((state) => state.close)
  const toggleWidget = useChatWidgetStore((state) => state.toggle)

  const inputRef = useRef<HTMLInputElement>(null)
  const [message, setMessage] = useState('')
  const [iconError, setIconError] = useState(false)

  useEffect(() => {
    if (!isOpen) {
      return
    }

    const focusTimer = window.setTimeout(() => {
      inputRef.current?.focus()
    }, 0)

    return () => {
      window.clearTimeout(focusTimer)
    }
  }, [isOpen])

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

  const handleSubmit = useCallback(
    (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault()
      if (!message.trim()) {
        return
      }
      setMessage('')
    },
    [message]
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

  const handleIconError = useCallback(() => {
    setIconError(true)
  }, [])

  return (
    <>
      <Button
        type="button"
        onClick={toggleWidget}
        aria-label="Open chat"
        aria-expanded={isOpen}
        aria-controls={CHAT_WIDGET_PANEL_ID}
        className={cn(
          'fixed z-[110] flex items-center gap-2 rounded-full bg-black px-5 py-3 text-sm font-medium text-white shadow-lg transition-all hover:shadow-xl focus-visible:ring-2 focus-visible:ring-white/60 focus-visible:ring-offset-2 focus-visible:ring-offset-black',
          'active:scale-[0.98]'
        )}
        style={buttonSafeAreaStyle}
      >
        {!iconError ? (
          <img
            src="/ai.png"
            alt="AI icon"
            className="h-6 w-6 rounded-full bg-white/10 object-contain"
            onError={handleIconError}
          />
        ) : (
          <span className="flex items-center gap-1 rounded-full bg-white/10 px-2 py-1">
            <Headphones className="h-4 w-4" />
            <Mic className="h-4 w-4" />
          </span>
        )}
        <span className="text-sm font-semibold">Talk with Us</span>
      </Button>

      <Dialog open={isOpen} onOpenChange={handleOpenChange}>
        <DialogContent
          id={CHAT_WIDGET_PANEL_ID}
          aria-labelledby={CHAT_WIDGET_TITLE_ID}
          containerClassName="p-0"
          className="w-[min(360px,calc(100vw-3rem))] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
          style={panelSafeAreaStyle}
        >
          <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
            <div className="flex items-center gap-3">
              {!iconError ? (
                <img
                  src="/ai.png"
                  alt="AI icon"
                  className="h-8 w-8 rounded-full bg-white object-contain"
                  onError={handleIconError}
                />
              ) : (
                <span className="flex items-center gap-2 rounded-full bg-black/80 px-3 py-1 text-white">
                  <Headphones className="h-4 w-4" />
                  <Mic className="h-4 w-4" />
                </span>
              )}
              <div>
                <p id={CHAT_WIDGET_TITLE_ID} className="text-sm font-semibold text-slate-900">
                  Talk with Us
                </p>
                <p className="text-xs text-slate-500">Choose voice or text to communicate</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                aria-label="Minimize chat"
                onClick={toggleWidget}
                className="rounded-full p-1 text-slate-500 transition-colors hover:bg-slate-200 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400"
              >
                <Minus className="h-4 w-4" />
              </button>
              <button
                type="button"
                aria-label="Close chat"
                onClick={closeWidget}
                className="rounded-full p-1 text-slate-500 transition-colors hover:bg-slate-200 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="flex h-[380px] flex-col bg-white">
            <div className="flex-1 overflow-y-auto px-4 py-3">
              <div className="space-y-3 text-xs text-slate-500">
                <div className="rounded-lg bg-slate-100 p-3 text-slate-600">
                  👋 Hi there! We&apos;re here to help. Use voice or text to reach out — a real teammate will reply soon.
                </div>
                <div className="rounded-lg bg-black p-3 text-white">
                  Tip: share your student ID or topic so we can route you faster.
                </div>
              </div>
            </div>

            <div className="border-t border-slate-200 bg-white px-4 py-3">
              <form className="flex items-end gap-2" onSubmit={handleSubmit}>
                <Input
                  ref={inputRef}
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Type your message..."
                  className="min-h-[42px] flex-1 resize-none"
                />
                <Button type="submit" size="icon" className="h-10 w-10 shrink-0 bg-black hover:bg-black/90">
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}



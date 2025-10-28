import { Bot } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function FloatingAIButton() {
  return (
    <Button
      size="icon"
      className="fixed bottom-8 right-8 h-14 w-14 rounded-full shadow-lg bg-primary hover:bg-primary/90 hover:scale-110 transition-all z-50"
      aria-label="AI 助手"
    >
      <Bot className="h-6 w-6" />
    </Button>
  )
}


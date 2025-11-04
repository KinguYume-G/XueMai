import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ErrorStateProps {
  message: string
  onRetry?: () => void
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="rounded-full bg-destructive/10 p-3 mb-4">
        <AlertCircle className="h-8 w-8 text-destructive" />
      </div>
      <h3 className="text-lg font-semibold mb-2">出错了</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-md">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline">
          重试
        </Button>
      )}
    </div>
  )
}

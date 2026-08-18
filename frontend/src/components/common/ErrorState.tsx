import { AlertCircle } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'

interface ErrorStateProps {
  message: string
  onRetry?: () => void
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  const { t } = useTranslation()
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="rounded-full bg-destructive/10 p-3 mb-4">
        <AlertCircle className="h-8 w-8 text-destructive" />
      </div>
      <h3 className="text-lg font-semibold mb-2">{t('common.errorTitle')}</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-md">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline">
          {t('common.retry')}
        </Button>
      )}
    </div>
  )
}

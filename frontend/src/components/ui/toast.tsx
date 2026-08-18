import { useEffect } from 'react'
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastProps {
  id: string
  type: ToastType
  message: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
  onClose: () => void
}

const Toast: React.FC<ToastProps> = ({ type, message, duration = 5000, action, onClose }) => {
  const { t } = useTranslation()
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <AlertCircle className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />,
  }

  const colors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  }

  const iconColors = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500',
  }

  return (
    <div
      className={`flex items-center gap-3 p-4 rounded-lg border shadow-lg ${colors[type]} animate-slide-up`}
      role="alert"
    >
      <div className={`flex-shrink-0 ${iconColors[type]}`}>
        {icons[type]}
      </div>
      <div className="flex-1 text-sm font-medium">
        {message}
      </div>
      {action && (
        <button
          onClick={action.onClick}
          className="flex-shrink-0 text-sm font-semibold underline hover:no-underline"
        >
          {action.label}
        </button>
      )}
      <button
        onClick={onClose}
        className="flex-shrink-0 hover:opacity-70 transition-opacity"
        aria-label={t('chat.actions.close')}
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

interface ToastContainerProps {
  toasts: Omit<ToastProps, 'onClose'>[]
  onRemove: (id: string) => void
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 max-w-md">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={() => onRemove(toast.id)} />
      ))}
    </div>
  )
}

export default Toast







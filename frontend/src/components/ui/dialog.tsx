import * as React from 'react'
import { createPortal } from 'react-dom'
import { cn } from '@/lib/utils'

interface DialogContextValue {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const DialogContext = React.createContext<DialogContextValue | undefined>(undefined)

function useDialogContext(component: string) {
  const context = React.useContext(DialogContext)
  if (!context) {
    throw new Error(`${component} must be used within Dialog`)
  }
  return context
}

export interface DialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

export const Dialog: React.FC<DialogProps> = ({ open: controlledOpen, onOpenChange, children }) => {
  const [uncontrolledOpen, setUncontrolledOpen] = React.useState(false)
  const fallbackOnOpenChange = React.useCallback((value: boolean) => {
    setUncontrolledOpen(value)
  }, [])

  const open = controlledOpen ?? uncontrolledOpen
  const handleOpenChange = onOpenChange ?? fallbackOnOpenChange

  const contextValue = React.useMemo(
    () => ({
      open,
      onOpenChange: handleOpenChange,
    }),
    [open, handleOpenChange]
  )

  return <DialogContext.Provider value={contextValue}>{children}</DialogContext.Provider>
}

const isBrowser = typeof window !== 'undefined' && typeof document !== 'undefined'

const DialogPortal: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  if (!isBrowser) {
    return null
  }
  return createPortal(children, document.body)
}

export const DialogOverlay = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    const { open, onOpenChange } = useDialogContext('DialogOverlay')

    if (!open) {
      return null
    }

    return (
      <DialogPortal>
        <div
          ref={ref}
          aria-hidden="true"
          className={cn('fixed inset-0 z-[104] bg-black/40', className)}
          onClick={() => onOpenChange(false)}
          {...props}
        />
      </DialogPortal>
    )
  }
)
DialogOverlay.displayName = 'DialogOverlay'

interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  containerClassName?: string
}

export const DialogContent = React.forwardRef<HTMLDivElement, DialogContentProps>(
  ({ className, containerClassName, children, ...props }, ref) => {
    const { open } = useDialogContext('DialogContent')

    if (!open) {
      return null
    }

    const content = (
      <div
        className={cn(
          'fixed inset-0 z-[105] flex items-end justify-end p-4 pointer-events-none',
          containerClassName
        )}
      >
        <div
          ref={ref}
          role="dialog"
          aria-modal="true"
          className={cn('pointer-events-auto', className)}
          {...props}
        >
          {children}
        </div>
      </div>
    )

    return <DialogPortal>{content}</DialogPortal>
  }
)
DialogContent.displayName = 'DialogContent'



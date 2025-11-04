import { Inbox } from 'lucide-react'

interface EmptyStateProps {
  message: string
  icon?: React.ReactNode
}

export default function EmptyState({ message, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="rounded-full bg-secondary p-3 mb-4">
        {icon || <Inbox className="h-8 w-8 text-muted-foreground" />}
      </div>
      <p className="text-sm text-muted-foreground max-w-md">{message}</p>
    </div>
  )
}

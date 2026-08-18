import { useTranslation } from 'react-i18next'

interface ConfirmDialogProps {
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  confirming?: boolean
  onConfirm: () => void
  onCancel: () => void
}

/**
 * Small centered confirm modal, matching the inline-overlay pattern already
 * used for the unbookmark confirmation in BookmarkedCommunityCard.
 */
export default function ConfirmDialog({
  title,
  description,
  confirmLabel,
  cancelLabel,
  confirming = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const { t } = useTranslation()
  const resolvedConfirmLabel = confirmLabel ?? t('common.ok')
  const resolvedCancelLabel = cancelLabel ?? t('common.cancel')
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="mx-4 max-w-sm rounded-lg bg-white p-6">
        <h3 className="mb-2 text-lg font-semibold">{title}</h3>
        {description && <p className="mb-6 text-sm text-gray-600">{description}</p>}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={confirming}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 transition-colors hover:bg-gray-50 disabled:opacity-50"
          >
            {resolvedCancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={confirming}
            className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-white transition-colors hover:bg-red-700 disabled:opacity-50"
          >
            {confirming ? t('common.processing') : resolvedConfirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

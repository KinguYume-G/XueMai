import { Link, useLocation } from 'react-router-dom'
import { ArrowLeft, Home } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function NotFound() {
  const { t } = useTranslation()
  const location = useLocation()

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
      <section className="w-full max-w-lg rounded-2xl border bg-white p-8 text-center shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">404</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-900">{t('notFound.title')}</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          {t('notFound.descriptionBefore')} <code className="rounded bg-slate-100 px-1.5 py-0.5">{location.pathname}</code>
          {t('notFound.descriptionAfter')}
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            <ArrowLeft className="h-4 w-4" />
            {t('notFound.goBack')}
          </button>
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            <Home className="h-4 w-4" />
            {t('notFound.backHome')}
          </Link>
        </div>
      </section>
    </main>
  )
}

import { useEffect, useState } from 'react'
import { Plane, Calendar } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { exchangeApi } from '@/services/api/exchange'
import type { ExchangeProgram } from '@/types/api'

export default function ExchangeRemindersCard() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [reminders, setReminders] = useState<ExchangeProgram[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchReminders() {
      try {
        const data = await exchangeApi.getUpcoming(2)
        setReminders(data)
      } catch (error) {
        console.error('Fetch reminders error:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchReminders()
  }, [])

  const handleReminderClick = (reminder: ExchangeProgram) => {
    navigate(`/exchange-programs/${reminder.id}`)
  }

  if (loading) {
    return (
      <Card className="rounded-xl border shadow-sm">
        <CardHeader className="pb-3 px-4 pt-4">
          <CardTitle className="flex items-center gap-2 text-base font-semibold">
            <Plane className="h-5 w-5 text-primary" />
            {t('rightAside.exchangeReminders.title')}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <p className="text-sm text-gray-400">{t('rightAside.exchangeReminders.loading')}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="rounded-xl border shadow-sm">
      <CardHeader className="pb-3 px-4 pt-4">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <Plane className="h-5 w-5 text-primary" />
          {t('rightAside.exchangeReminders.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-0 px-2 pb-2">
        {reminders.length === 0 ? (
          <p className="text-sm text-gray-400 px-3 py-2.5">{t('rightAside.exchangeReminders.empty')}</p>
        ) : (
          reminders.map((reminder, index) => (
            <div key={reminder.id}>
              {index > 0 && <Separator className="my-2" />}
              <button
                onClick={() => handleReminderClick(reminder)}
                className="flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left hover:bg-secondary/80 transition-colors"
              >
                <Calendar className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-primary hover:underline line-clamp-1">
                      {t('rightAside.exchangeReminders.program', { university: reminder.university })}
                    </span>
                    {index === 1 && (
                      <span className="bg-green-500 text-white text-xs px-2 py-0.5 rounded flex-shrink-0">
                        {t('rightAside.exchangeReminders.new')}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-red-500">{t('rightAside.exchangeReminders.deadline', { date: reminder.deadline })}</div>
                </div>
              </button>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}

import { useEffect, useState } from 'react'
import { Flame } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api/client'

interface Topic {
  name: string
  post_count: number
}

export default function HotTopicsCard() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [topics, setTopics] = useState<Topic[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient.get<Topic[]>('/topics/hot/', { params: { limit: 4, window: 'all' } })
      .then(setTopics)
      .catch(() => setTopics([]))
      .finally(() => setLoading(false))
  }, [])

  const handleTopicClick = (topic: Topic) => {
    navigate(`/search?q=${encodeURIComponent(topic.name)}`)
  }

  return (
    <Card className="rounded-xl border shadow-sm">
      <CardHeader className="pb-3 px-4 pt-4">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <Flame className="h-5 w-5 text-orange-500" />
          {t('rightAside.hotTopics.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-0 px-2 pb-2">
        {loading ? <p className="px-3 py-3 text-sm text-muted-foreground">{t('rightAside.hotTopics.loading')}</p> : null}
        {!loading && topics.length === 0 ? <p className="px-3 py-3 text-sm text-muted-foreground">{t('rightAside.hotTopics.empty')}</p> : null}
        {topics.map((topic) => (
          <button
            key={topic.name}
            onClick={() => handleTopicClick(topic)}
            className="flex w-full flex-col items-start rounded-lg px-3 py-2.5 text-sm hover:bg-secondary/80 transition-colors text-left"
          >
            <span className="font-medium text-primary hover:underline">
              #{topic.name}
            </span>
            <span className="text-xs text-muted-foreground">
              {t('rightAside.hotTopics.postCount', { count: topic.post_count })}
            </span>
          </button>
        ))}
      </CardContent>
    </Card>
  )
}

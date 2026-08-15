import { useEffect, useState } from 'react'
import { Flame } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { forumsApi } from '@/services/api/forums'

interface Topic {
  name: string
  post_count: number
}

export default function HotTopicsCard() {
  const navigate = useNavigate()
  const [topics, setTopics] = useState<Topic[]>([])

  useEffect(() => {
    forumsApi.getHotTopics(4).then(setTopics).catch(() => setTopics([]))
  }, [])

  const handleTopicClick = (topic: Topic) => {
    // 跳转到社区页面，并筛选该标签
    navigate(`/?tag=${encodeURIComponent(topic.name)}`)
  }

  return (
    <Card className="rounded-xl border shadow-sm">
      <CardHeader className="pb-3 px-4 pt-4">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <Flame className="h-5 w-5 text-orange-500" />
          热门话题
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-0 px-2 pb-2">
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
              {topic.post_count} 帖子
            </span>
          </button>
        ))}
        {topics.length === 0 && <p className="px-3 py-2 text-sm text-muted-foreground">暂无热门话题</p>}
      </CardContent>
    </Card>
  )
}

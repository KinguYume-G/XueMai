import { Flame } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Topic {
  id: string
  name: string
  tag: string
  postCount: number
}

const topics: Topic[] = [
  { id: '1', name: 'AI论文写作技巧', tag: '#AI论文写作技巧', postCount: 15 },
  { id: '2', name: '马来西亚实习指南', tag: '#马来西亚实习指南', postCount: 12 },
  { id: '3', name: '跨文化交流经验', tag: '#跨文化交流经验', postCount: 8 },
  { id: '4', name: '2024秋季交换信息', tag: '#2024秋季交换信息', postCount: 6 },
]

export default function HotTopicsCard() {
  const navigate = useNavigate()

  const handleTopicClick = (topic: Topic) => {
    // 跳转到社区页面，并筛选该标签
    navigate(`/?tag=${encodeURIComponent(topic.tag)}`)
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
            key={topic.id}
            onClick={() => handleTopicClick(topic)}
            className="flex w-full flex-col items-start rounded-lg px-3 py-2.5 text-sm hover:bg-secondary/80 transition-colors text-left"
          >
            <span className="font-medium text-primary hover:underline">
              {topic.tag}
            </span>
            <span className="text-xs text-muted-foreground">
              {topic.postCount} 帖子
            </span>
          </button>
        ))}
      </CardContent>
    </Card>
  )
}

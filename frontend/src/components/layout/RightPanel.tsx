import { useEffect, useState } from 'react'
import { ChevronRight, Lock, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { getSchools, getTopics, getExchangePrograms } from '@/services/mock'
import type { School, Topic, ExchangeProgram } from '@/types/post'

export default function RightPanel() {
  const [schools, setSchools] = useState<School[]>([])
  const [topics, setTopics] = useState<Topic[]>([])
  const [programs, setPrograms] = useState<ExchangeProgram[]>([])

  useEffect(() => {
    getSchools().then(setSchools)
    getTopics().then(setTopics)
    getExchangePrograms().then(setPrograms)
  }, [])

  return (
    <aside className="fixed right-0 top-16 bottom-0 w-80 overflow-y-auto p-6 space-y-4">
      {/* School Zones Card */}
      <Card className="border shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">学校专区</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          {schools.map((school) => (
            <button
              key={school.id}
              className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm hover:bg-secondary/80 transition-colors"
            >
              <div className="flex items-center gap-2">
                {school.isLocked && <Lock className="h-4 w-4 text-muted-foreground" />}
                <span className={school.isLocked ? 'text-muted-foreground' : 'font-medium'}>
                  {school.name}
                </span>
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </button>
          ))}
        </CardContent>
      </Card>

      {/* Hot Topics Card */}
      <Card className="border shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">热门话题</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {topics.map((topic) => (
            <div key={topic.id} className="flex items-start gap-2">
              <span className="text-xl">#</span>
              <button className="text-sm text-left hover:text-primary transition-colors">
                {topic.title}
              </button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Exchange Programs Card */}
      <Card className="border shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">交换项目提醒</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {programs.map((program, index) => (
            <div key={program.id}>
              {index > 0 && <Separator className="mb-3" />}
              <button className="flex items-start gap-3 text-left w-full hover:bg-secondary/50 -mx-2 px-2 py-1 rounded-lg transition-colors">
                <Calendar className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium mb-0.5">{program.title}</div>
                  <div className="text-xs text-muted-foreground">{program.deadline}</div>
                </div>
              </button>
            </div>
          ))}
        </CardContent>
      </Card>
    </aside>
  )
}


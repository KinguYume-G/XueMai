import { useEffect, useState } from 'react'
import { ChevronRight, Lock, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

// 临时类型定义（待后端API完善后移除）
interface School {
  id: string
  name: string
  isLocked: boolean
}

interface Topic {
  id: string
  title: string
  tag: string
}

interface ExchangeProgram {
  id: string
  title: string
  deadline: string
}

export default function RightPanel() {
  const [schools] = useState<School[]>([
    { id: 'apu', name: 'APU 专区', isLocked: false },
    { id: 'tsinghua', name: '清华大学专区', isLocked: true },
    { id: 'pku', name: '北京大学专区', isLocked: true }
  ])
  
  const [topics] = useState<Topic[]>([
    { id: '1', title: 'AI论文写作技巧', tag: '#AI论文写作技巧' },
    { id: '2', title: '马来西亚实习机指南', tag: '#马来西亚实习机指南' },
    { id: '3', title: '跨文化交流经验', tag: '#跨文化交流经验' },
    { id: '4', title: '2024秋季交换信息', tag: '#2024秋季交换信息' }
  ])
  
  const [programs] = useState<ExchangeProgram[]>([
    { id: '1', title: '新加坡国立大学交换', deadline: '截止日期: 2024-10-15' },
    { id: '2', title: '香港大学暑期项目', deadline: '截止日期: 2024-11-01' }
  ])

  // TODO: 替换为真实API调用
  // useEffect(() => {
  //   const loadData = async () => {
  //     try {
  //       const [schoolsData, topicsData, programsData] = await Promise.all([
  //         apiClient.get('/schools/'),
  //         apiClient.get('/topics/'),
  //         apiClient.get('/exchange_programs/')
  //       ])
  //       setSchools(schoolsData)
  //       setTopics(topicsData)
  //       setPrograms(programsData)
  //     } catch (error) {
  //       console.error('Failed to load panel data:', error)
  //     }
  //   }
  //   loadData()
  // }, [])

  useEffect(() => {
    // 暂时不加载数据，使用静态内容
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


import { GraduationCap, BookOpen, MessageCircle, Users, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

// 统计数据
interface StatCard {
  icon: React.ReactNode
  value: string
  label: string
  color: string
}

// 学院数据
interface College {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  color: string
  specialtyCount: number
  topicCount: number
  onlineCount: number
  path: string
}

// 热门话题
interface HotTopic {
  icon: string
  name: string
  count: number
  color: string
}

const statCards: StatCard[] = [
  {
    icon: <GraduationCap className="h-12 w-12" />,
    value: '6',
    label: '学院',
    color: 'text-blue-500',
  },
  {
    icon: <BookOpen className="h-12 w-12" />,
    value: '60+',
    label: '专业',
    color: 'text-green-500',
  },
  {
    icon: <MessageCircle className="h-12 w-12" />,
    value: '4.1k',
    label: '话题',
    color: 'text-orange-500',
  },
  {
    icon: <Users className="h-12 w-12" />,
    value: '12k+',
    label: '活跃用户',
    color: 'text-purple-500',
  },
]

const colleges: College[] = [
  {
    id: 'cs',
    name: '计算机学院',
    description: '软件工程、人工智能、网络安全',
    icon: <GraduationCap className="h-8 w-8 text-white" />,
    color: 'bg-blue-500',
    specialtyCount: 12,
    topicCount: 1200,
    onlineCount: 44,
    path: '/forums/cs',
  },
  {
    id: 'business',
    name: '商学院',
    description: '工商管理、市场营销、会计学',
    icon: <BookOpen className="h-8 w-8 text-white" />,
    color: 'bg-green-500',
    specialtyCount: 8,
    topicCount: 856,
    onlineCount: 32,
    path: '/forums/business',
  },
  {
    id: 'engineering',
    name: '工程学院',
    description: '机械工程、电子工程、土木工程',
    icon: <GraduationCap className="h-8 w-8 text-white" />,
    color: 'bg-orange-500',
    specialtyCount: 10,
    topicCount: 923,
    onlineCount: 28,
    path: '/forums/engineering',
  },
  {
    id: 'design',
    name: '设计学院',
    description: '视觉传达、产品设计、数字媒体',
    icon: <BookOpen className="h-8 w-8 text-white" />,
    color: 'bg-purple-500',
    specialtyCount: 6,
    topicCount: 645,
    onlineCount: 19,
    path: '/forums/design',
  },
  {
    id: 'medical',
    name: '医学院',
    description: '临床医学、护理学、药学',
    icon: <GraduationCap className="h-8 w-8 text-white" />,
    color: 'bg-red-500',
    specialtyCount: 9,
    topicCount: 734,
    onlineCount: 25,
    path: '/forums/medical',
  },
  {
    id: 'arts',
    name: '文学院',
    description: '汉语言文学、新闻学、历史学',
    icon: <BookOpen className="h-8 w-8 text-white" />,
    color: 'bg-indigo-500',
    specialtyCount: 7,
    topicCount: 512,
    onlineCount: 15,
    path: '/forums/arts',
  },
]

const hotTopics: HotTopic[] = [
  { icon: '📚', name: '课程资料', count: 567, color: 'bg-blue-50 text-blue-600 hover:bg-blue-100' },
  { icon: '❓', name: '问答互助', count: 423, color: 'bg-red-50 text-red-600 hover:bg-red-100' },
  { icon: '💡', name: '经验分享', count: 345, color: 'bg-orange-50 text-orange-600 hover:bg-orange-100' },
  { icon: '🔬', name: '学术研究', count: 234, color: 'bg-purple-50 text-purple-600 hover:bg-purple-100' },
]

export default function Forums() {
  const navigate = useNavigate()

  const handleCollegeClick = (college: College) => {
    navigate(college.path)
  }

  const handleTopicClick = (topic: HotTopic) => {
    // 跳转到该话题的讨论页面
    navigate(`/forums/topics/${encodeURIComponent(topic.name)}`)
  }

  // 生成随机头像颜色
  const getRandomAvatarColor = (index: number) => {
    const colors = ['bg-blue-500', 'bg-green-500', 'bg-orange-500', 'bg-purple-500', 'bg-pink-500']
    return colors[index % colors.length]
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="text-sm text-muted-foreground">
        首页 &gt; 专业论坛
      </div>

      {/* Page Header */}
      <div>
        <h1 className="text-[32px] font-bold leading-tight text-gray-900">专业论坛</h1>
        <p className="mt-2 text-base text-gray-600">
          选择你的学院，与同专业的同学交流学习认知经验
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <Card
            key={index}
            className="rounded-xl border shadow-sm hover:shadow-md transition-shadow"
          >
            <CardContent className="flex flex-col items-center justify-center p-6 h-[120px]">
              <div className={stat.color}>{stat.icon}</div>
              <div className="mt-2 text-[32px] font-bold leading-tight">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* College Cards Grid */}
      <div className="grid grid-cols-3 gap-4">
        {colleges.map((college) => (
          <Card
            key={college.id}
            className="rounded-xl border shadow-sm hover:shadow-md transition-shadow cursor-pointer group"
            onClick={() => handleCollegeClick(college)}
          >
            <CardContent className="p-5 h-[180px] flex flex-col">
              {/* Top Section */}
              <div className="flex items-start gap-3 mb-4">
                <div className={`${college.color} rounded-full p-3 shrink-0`}>
                  {college.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold mb-1">{college.name}</h3>
                  <p className="text-sm text-gray-600 line-clamp-1">{college.description}</p>
                </div>
              </div>

              {/* Stats Section */}
              <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
                <div>
                  <span className="text-gray-600">专业数量</span>
                </div>
                <div className="text-right">
                  <span className="font-medium">{college.specialtyCount}个专业</span>
                </div>
                <div>
                  <span className="text-gray-600">讨论话题</span>
                </div>
                <div className="text-right">
                  <span className="font-medium">{college.topicCount}个话题</span>
                </div>
              </div>

              {/* Bottom Section */}
              <div className="flex items-center justify-between mt-auto">
                <div className="flex items-center gap-2">
                  {/* Avatar Stack */}
                  <div className="flex -space-x-2">
                    {[0, 1, 2].map((i) => (
                      <Avatar key={i} className="h-8 w-8 border-2 border-white">
                        <AvatarFallback className={getRandomAvatarColor(i)}>
                          <span className="text-white text-xs">U</span>
                        </AvatarFallback>
                      </Avatar>
                    ))}
                  </div>
                  <span className="text-sm text-gray-600">+{college.onlineCount}人在线</span>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Hot Topics */}
      <div>
        <h2 className="text-xl font-bold mb-4">热门话题</h2>
        <div className="grid grid-cols-4 gap-4">
          {hotTopics.map((topic, index) => (
            <button
              key={index}
              onClick={() => handleTopicClick(topic)}
              className={`${topic.color} rounded-xl px-6 py-4 text-left transition-all`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{topic.icon}</span>
                <span className="font-semibold">{topic.name}</span>
              </div>
              <div className="text-sm opacity-80">{topic.count}个帖子</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

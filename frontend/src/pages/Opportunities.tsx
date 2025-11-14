import { useState } from 'react'
import { MapPin, DollarSign, Home, Calendar, Users, Bookmark, BookmarkCheck, Gem } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

type TabType = 'internship' | 'startup'

interface Internship {
  id: string
  company: string
  position: string
  logo: string
  location: string
  salary: string
  remote: boolean
  skills: string[]
  description: string
  publishedDays: number
  applicantCount: number
}

interface Startup {
  id: string
  company: string
  project: string
  logo: string
  location: string
  equity: string
  stage?: string
  tags: string[]
  description: string
  publishedDays: number
  interestedCount: number
}

const internships: Internship[] = [
  {
    id: '1',
    company: '腾讯',
    position: '前端开发实习生',
    logo: '🐧',
    location: '深圳',
    salary: '¥5000-8000/月',
    remote: true,
    skills: ['React', 'TypeScript', 'Vue'],
    description: '负责前端开发产品设计参与，与设计师和后端工程师协作完成产品...',
    publishedDays: 2,
    applicantCount: 89,
  },
  {
    id: '2',
    company: '阿里巴巴',
    position: 'AI算法实习生',
    logo: '🟠',
    location: '杭州',
    salary: '¥6000-10000/月',
    remote: false,
    skills: ['Python', 'TensorFlow', 'PyTorch'],
    description: '参与AI算法研发，负责模型训练和优化，推动智能产品落地...',
    publishedDays: 5,
    applicantCount: 156,
  },
  {
    id: '3',
    company: '字节跳动',
    position: '产品经理实习生',
    logo: '🎵',
    location: '北京',
    salary: '¥4000-7000/月',
    remote: false,
    skills: ['产品设计', '数据分析', 'Axure'],
    description: '参与产品规划和设计，协调跨部门资源，推动产品迭代...',
    publishedDays: 3,
    applicantCount: 67,
  },
]

const startups: Startup[] = [
  {
    id: '1',
    company: '智学科技',
    project: 'AI教育创业项目',
    logo: '🤖',
    location: '上海',
    equity: '0.5-2%',
    tags: ['AI', '教育', '产品开发'],
    description: '专注于AI驱动的个性化教育平台，寻找技术合伙人...',
    publishedDays: 5,
    interestedCount: 23,
  },
  {
    id: '2',
    company: '数字金融',
    project: '金融科技创业团队',
    logo: '💰',
    location: '深圳',
    equity: '1-3%',
    stage: 'Pre-A轮',
    tags: ['金融科技', '区块链', '移动支付'],
    description: '打造新一代数字金融服务平台，已获千万级天使轮融资...',
    publishedDays: 7,
    interestedCount: 34,
  },
]

export default function Opportunities() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<TabType>('internship')
  const [searchInput, setSearchInput] = useState('')
  const [locationFilter, setLocationFilter] = useState('')
  const [fieldFilter, setFieldFilter] = useState('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [bookmarkedItems, setBookmarkedItems] = useState<Set<string>>(new Set(['1', '2']))

  const toggleBookmark = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setBookmarkedItems((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-[32px] font-bold leading-tight text-gray-900">实习 & 创业机会</h1>
        <p className="mt-2 text-base text-gray-600">
          发现职业发展和创业机遇
        </p>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-0 border-b">
        <button
          onClick={() => setActiveTab('internship')}
          className={`
            px-6 py-3 text-sm font-medium transition-colors relative
            ${activeTab === 'internship' ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}
          `}
        >
          实习机会
          {activeTab === 'internship' && (
            <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-primary" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('startup')}
          className={`
            px-6 py-3 text-sm font-medium transition-colors relative
            ${activeTab === 'startup' ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}
          `}
        >
          创业机会
          {activeTab === 'startup' && (
            <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-primary" />
          )}
        </button>
      </div>

      {/* Filters */}
      {activeTab === 'internship' ? (
        <div className="flex items-center gap-3">
          <Input
            placeholder="搜索职位或公司..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="h-10 flex-1 rounded-lg border-gray-300 focus:border-primary"
          />
          <select
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            className="h-10 w-[180px] rounded-lg border border-gray-300 px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">全部地点</option>
            <option value="北京">北京</option>
            <option value="上海">上海</option>
            <option value="深圳">深圳</option>
            <option value="杭州">杭州</option>
          </select>
          <select
            value={fieldFilter}
            onChange={(e) => setFieldFilter(e.target.value)}
            className="h-10 w-[180px] rounded-lg border border-gray-300 px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">全部领域</option>
            <option value="技术">技术</option>
            <option value="产品">产品</option>
            <option value="设计">设计</option>
            <option value="运营">运营</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input
              type="checkbox"
              checked={remoteOnly}
              onChange={(e) => setRemoteOnly(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <Home className="h-4 w-4" />
            <span>支持远程</span>
          </label>
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <Input
            placeholder="搜索职位或公司..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="h-10 flex-1 rounded-lg border-gray-300 focus:border-primary"
          />
          <select
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            className="h-10 w-[180px] rounded-lg border border-gray-300 px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">全部地点</option>
            <option value="北京">北京</option>
            <option value="上海">上海</option>
            <option value="深圳">深圳</option>
            <option value="杭州">杭州</option>
          </select>
          <select
            value={fieldFilter}
            onChange={(e) => setFieldFilter(e.target.value)}
            className="h-10 w-[180px] rounded-lg border border-gray-300 px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">全部领域</option>
            <option value="技术">技术</option>
            <option value="金融">金融</option>
            <option value="教育">教育</option>
            <option value="健康">健康</option>
          </select>
        </div>
      )}

      {/* Content */}
      <div className="space-y-4">
        {activeTab === 'internship' ? (
          // Internship Cards
          internships.map((item) => {
            const isBookmarked = bookmarkedItems.has(item.id)
            return (
              <Card
                key={item.id}
                className="rounded-xl border shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/internships/${item.id}`)}
              >
                <CardContent className="p-5 min-h-[180px]">
                  <div className="flex items-start gap-4">
                    {/* Logo */}
                    <div className="w-16 h-16 rounded-lg border border-gray-200 flex items-center justify-center text-3xl shrink-0 bg-white">
                      {item.logo}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="text-lg font-semibold mb-1">{item.position}</h3>
                          <p className="text-sm text-gray-600">{item.company}</p>
                        </div>
                        <button
                          onClick={(e) => toggleBookmark(item.id, e)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          {isBookmarked ? (
                            <BookmarkCheck className="h-5 w-5 text-primary fill-primary" />
                          ) : (
                            <Bookmark className="h-5 w-5 text-gray-400" />
                          )}
                        </button>
                      </div>

                      {/* Info Row */}
                      <div className="flex items-center gap-4 mb-3 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4 text-gray-400" />
                          <span>{item.location}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <DollarSign className="h-4 w-4 text-gray-400" />
                          <span>{item.salary}</span>
                        </div>
                        {item.remote && (
                          <div className="flex items-center gap-1">
                            <Home className="h-4 w-4 text-gray-400" />
                            <span>支持远程</span>
                          </div>
                        )}
                      </div>

                      {/* Skills */}
                      <div className="flex items-center gap-2 mb-3">
                        {item.skills.map((skill, index) => (
                          <Badge
                            key={index}
                            variant="secondary"
                            className="bg-blue-50 text-blue-600 hover:bg-blue-100"
                          >
                            {skill}
                          </Badge>
                        ))}
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                        {item.description}
                      </p>

                      {/* Footer */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4 text-gray-400" />
                            <span>发布{item.publishedDays}天前</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4 text-gray-400" />
                            <span>{item.applicantCount}人已申请</span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="default"
                            size="sm"
                            className="bg-primary hover:bg-primary/90"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/internships/${item.id}`)
                            }}
                          >
                            查看详情
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="border-primary text-primary hover:bg-primary/5"
                            onClick={(e) => {
                              e.stopPropagation()
                              // Handle apply
                            }}
                          >
                            投递简历
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })
        ) : (
          // Startup Cards
          startups.map((item) => {
            const isBookmarked = bookmarkedItems.has(item.id)
            return (
              <Card
                key={item.id}
                className="rounded-xl border shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/startups/${item.id}`)}
              >
                <CardContent className="p-5 min-h-[180px]">
                  <div className="flex items-start gap-4">
                    {/* Logo */}
                    <div className="w-16 h-16 rounded-lg border border-gray-200 flex items-center justify-center text-3xl shrink-0 bg-white">
                      {item.logo}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="text-lg font-semibold mb-1">{item.project}</h3>
                          <p className="text-sm text-gray-600">{item.company}</p>
                        </div>
                        <button
                          onClick={(e) => toggleBookmark(item.id, e)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          {isBookmarked ? (
                            <BookmarkCheck className="h-5 w-5 text-primary fill-primary" />
                          ) : (
                            <Bookmark className="h-5 w-5 text-gray-400" />
                          )}
                        </button>
                      </div>

                      {/* Info Row */}
                      <div className="flex items-center gap-4 mb-3 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4 text-gray-400" />
                          <span>{item.location}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Gem className="h-4 w-4 text-gray-400" />
                          <span>股权: {item.equity}</span>
                        </div>
                        {item.stage && (
                          <Badge
                            variant="secondary"
                            className="bg-green-50 text-green-600"
                          >
                            {item.stage}
                          </Badge>
                        )}
                      </div>

                      {/* Tags */}
                      <div className="flex items-center gap-2 mb-3">
                        {item.tags.map((tag, index) => (
                          <Badge
                            key={index}
                            variant="secondary"
                            className="bg-purple-50 text-purple-600 hover:bg-purple-100"
                          >
                            {tag}
                          </Badge>
                        ))}
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                        {item.description}
                      </p>

                      {/* Footer */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4 text-gray-400" />
                            <span>发布{item.publishedDays}天前</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4 text-gray-400" />
                            <span>{item.interestedCount}人感兴趣</span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="default"
                            size="sm"
                            className="bg-purple-600 hover:bg-purple-700"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/startups/${item.id}`)
                            }}
                          >
                            了解详情
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="border-purple-600 text-purple-600 hover:bg-purple-50"
                            onClick={(e) => {
                              e.stopPropagation()
                              // Handle interest
                            }}
                          >
                            表达兴趣
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })
        )}
      </div>
    </div>
  )
}

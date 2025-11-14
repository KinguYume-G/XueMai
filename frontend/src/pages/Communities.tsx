import { useState } from 'react'
import { Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface Community {
  id: string
  name: string
  memberCount: number
  description: string
  icon: string
  activeRate: number
  isJoined: boolean
  category: string
}

const communities: Community[] = [
  {
    id: '1',
    name: '游戏爱好者社区',
    memberCount: 512,
    description: '分享游戏心得、组队开黑、电竞交流',
    icon: '🎮',
    activeRate: 87,
    isJoined: true,
    category: 'hobby',
  },
  {
    id: '2',
    name: 'APU篮球社',
    memberCount: 234,
    description: '校内篮球爱好者聚集地，组织球赛和训练',
    icon: '🏀',
    activeRate: 92,
    isJoined: true,
    category: 'campus',
  },
  {
    id: '3',
    name: '音乐创作交流',
    memberCount: 167,
    description: '分享原创音乐、编曲技巧、乐器教学',
    icon: '🎵',
    activeRate: 78,
    isJoined: false,
    category: 'hobby',
  },
  {
    id: '4',
    name: 'KL留学生互助',
    memberCount: 892,
    description: '吉隆坡留学生生活互助、资源分享',
    icon: '🌍',
    activeRate: 85,
    isJoined: false,
    category: 'city',
  },
  {
    id: '5',
    name: 'APU摄影社',
    memberCount: 325,
    description: '摄影技术交流、作品分享、外拍活动',
    icon: '📷',
    activeRate: 73,
    isJoined: false,
    category: 'campus',
  },
  {
    id: '6',
    name: '编程学习小组',
    memberCount: 456,
    description: '代码分享、技术讨论、项目协作',
    icon: '💻',
    activeRate: 89,
    isJoined: false,
    category: 'study',
  },
]

type CategoryType = 'all' | 'hobby' | 'city' | 'campus' | 'study'

const categories = [
  { key: 'all', label: '全部' },
  { key: 'hobby', label: '兴趣爱好' },
  { key: 'city', label: '城市同乡' },
  { key: 'campus', label: '校内社团' },
  { key: 'study', label: '学习小组' },
] as const

export default function Communities() {
  const navigate = useNavigate()
  const [activeCategory, setActiveCategory] = useState<CategoryType>('all')
  const [communityList, setCommunityList] = useState(communities)

  const handleCreateCommunity = () => {
    navigate('/communities/create')
  }

  const handleJoinCommunity = (communityId: string) => {
    setCommunityList((prev) =>
      prev.map((c) =>
        c.id === communityId ? { ...c, isJoined: !c.isJoined } : c
      )
    )
  }

  const handleCommunityClick = (communityId: string) => {
    navigate(`/communities/${communityId}`)
  }

  const filteredCommunities =
    activeCategory === 'all'
      ? communityList
      : communityList.filter((c) => c.category === activeCategory)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[32px] font-bold leading-tight text-gray-900">社区</h1>
          <p className="mt-2 text-base text-gray-600">
            发现志同道合的伙伴
          </p>
        </div>
        <Button
          onClick={handleCreateCommunity}
          className="gap-2 bg-primary hover:bg-primary/90 h-10 px-6 rounded-lg"
        >
          <Plus className="h-4 w-4" />
          创建社区
        </Button>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-0 border-b">
        {categories.map((category) => (
          <button
            key={category.key}
            onClick={() => setActiveCategory(category.key as CategoryType)}
            className={`
              px-4 py-3 text-sm font-medium transition-colors relative
              ${
                activeCategory === category.key
                  ? 'text-primary'
                  : 'text-gray-600 hover:text-gray-900'
              }
            `}
          >
            {category.label}
            {activeCategory === category.key && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>
        ))}
      </div>

      {/* Community Cards Grid */}
      <div className="grid grid-cols-3 gap-4">
        {filteredCommunities.length === 0 ? (
          <div className="col-span-3 text-center py-12 text-gray-600">
            暂无社区
          </div>
        ) : (
          filteredCommunities.map((community) => (
            <Card
              key={community.id}
              className="rounded-xl border shadow-sm hover:shadow-md transition-shadow"
            >
              <CardContent className="p-5 flex flex-col items-center text-center min-h-[280px]">
                {/* Icon */}
                <div
                  className="w-16 h-16 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-3xl mb-4 cursor-pointer"
                  onClick={() => handleCommunityClick(community.id)}
                >
                  {community.icon}
                </div>

                {/* Name */}
                <h3
                  className="text-lg font-semibold mb-1 cursor-pointer hover:text-primary"
                  onClick={() => handleCommunityClick(community.id)}
                >
                  {community.name}
                </h3>

                {/* Member Count */}
                <p className="text-sm text-gray-600 mb-3">
                  {community.memberCount}成员
                </p>

                {/* Description */}
                <p className="text-sm text-gray-600 line-clamp-2 mb-4 flex-1">
                  {community.description}
                </p>

                {/* Stats */}
                <div className="flex items-center gap-1 text-sm text-gray-600 mb-4">
                  <span>{community.memberCount}成员</span>
                  <span>●</span>
                  <span>{community.activeRate}%活跃</span>
                </div>

                {/* Join Button */}
                <Button
                  onClick={() => handleJoinCommunity(community.id)}
                  variant={community.isJoined ? 'outline' : 'default'}
                  className={`w-full h-10 rounded-lg ${
                    community.isJoined
                      ? 'border-gray-300 text-gray-600 hover:bg-gray-50'
                      : 'bg-primary hover:bg-primary/90 text-white'
                  }`}
                >
                  {community.isJoined ? '已加入' : '加入社区'}
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

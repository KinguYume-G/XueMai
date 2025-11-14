import { useState } from 'react'
import { Users, Globe, BookOpen, Briefcase } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

type TabType = 'intro' | 'courses' | 'facilities' | 'activities'

export default function AboutAPU() {
  const [activeTab, setActiveTab] = useState<TabType>('intro')

  const statCards = [
    {
      icon: <Users className="h-12 w-12 text-purple-500" />,
      value: '12,000+',
      label: '在校学生',
    },
    {
      icon: <Globe className="h-12 w-12 text-blue-500" />,
      value: '8,000+',
      label: '国际学生',
    },
    {
      icon: <BookOpen className="h-12 w-12 text-green-500" />,
      value: '100+',
      label: '专业课程',
    },
    {
      icon: <Briefcase className="h-12 w-12 text-orange-500" />,
      value: '95%',
      label: '就业率',
    },
  ]

  return (
    <div className="space-y-6 -mx-6 -mt-8">
      {/* Hero Cover */}
      <div className="relative w-full h-[400px] bg-gradient-to-r from-blue-600 to-purple-600 flex flex-col items-center justify-center text-white">
        <h1 className="text-5xl font-bold mb-4">亚太科技大学 (APU)</h1>
        <p className="text-xl">Technology for Transformation</p>
      </div>

      {/* Tabs */}
      <div className="px-6">
        <div className="bg-white rounded-t-xl shadow-sm">
          <div className="flex items-center gap-0 border-b">
            <button
              onClick={() => setActiveTab('intro')}
              className={`
                px-6 py-4 text-sm font-medium transition-colors relative
                ${activeTab === 'intro' ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}
              `}
            >
              学校介绍
              {activeTab === 'intro' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('courses')}
              className={`
                px-6 py-4 text-sm font-medium transition-colors relative
                ${activeTab === 'courses' ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}
              `}
            >
              课程信息
              {activeTab === 'courses' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('facilities')}
              className={`
                px-6 py-4 text-sm font-medium transition-colors relative
                ${activeTab === 'facilities' ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}
              `}
            >
              设施服务
              {activeTab === 'facilities' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('activities')}
              className={`
                px-6 py-4 text-sm font-medium transition-colors relative
                ${activeTab === 'activities' ? 'text-primary' : 'text-gray-600 hover:text-gray-900'}
              `}
            >
              校园活动
              {activeTab === 'activities' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-b-xl shadow-sm p-6">
          {activeTab === 'intro' && (
            <div className="space-y-6">
              {/* Basic Info & Features */}
              <div className="grid grid-cols-2 gap-6">
                {/* Left Column */}
                <div>
                  <h2 className="flex items-center gap-2 text-lg font-semibold mb-4">
                    🏠 基本信息
                  </h2>
                  <div className="space-y-3 text-sm text-gray-600">
                    <div className="flex">
                      <span className="w-24 font-medium">成立时间:</span>
                      <span>1993年</span>
                    </div>
                    <div className="flex">
                      <span className="w-24 font-medium">地理位置:</span>
                      <span>马来西亚吉隆坡</span>
                    </div>
                    <div className="flex">
                      <span className="w-24 font-medium">校园面积:</span>
                      <span>23英亩</span>
                    </div>
                    <div className="flex">
                      <span className="w-24 font-medium">学校性质:</span>
                      <span>私立大学</span>
                    </div>
                  </div>
                </div>

                {/* Right Column */}
                <div>
                  <h2 className="flex items-center gap-2 text-lg font-semibold mb-4">
                    🎯 办学特色
                  </h2>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>英国同步传统优质大学合作办学</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>双学位课程，国际认可</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>多元文化国际化环境</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>产学研一体化教育模式</span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Statistics Cards */}
              <div className="grid grid-cols-4 gap-4">
                {statCards.map((stat, index) => (
                  <Card key={index} className="rounded-xl border shadow-sm">
                    <CardContent className="flex flex-col items-center justify-center p-5 h-[140px]">
                      {stat.icon}
                      <div className="mt-3 text-[28px] font-bold leading-tight">
                        {stat.value}
                      </div>
                      <div className="text-sm text-gray-600">{stat.label}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Mission */}
              <div className="space-y-4">
                <h2 className="flex items-center gap-2 text-xl font-semibold">
                  🎯 办学使命
                </h2>
                <p className="text-base text-gray-600 leading-relaxed">
                  培养具有全球视野、创新精神和实践能力的高素质人才。为亚太地区经济社会发展培养高端技术与管理人才，通过优质的教育资源和国际化学习环境，帮助学生实现个人价值与职业目标。
                </p>
              </div>

              {/* Vision */}
              <div className="space-y-4">
                <h2 className="flex items-center gap-2 text-xl font-semibold">
                  ⭐ 发展愿景
                </h2>
                <p className="text-base text-gray-600 leading-relaxed">
                  成为亚太地区领先的科技大学，在计算机科学、工程技术、商业管理等领域享有国际声誉，致力于推动教育创新、培养适应未来需求的综合型人才。
                </p>
              </div>
            </div>
          )}

          {activeTab === 'courses' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">课程信息</h2>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">本科课程</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>计算机科学与软件工程</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>人工智能与数据科学</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>网络安全与信息保障</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>商业管理与市场营销</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>会计与金融</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">研究生课程</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>计算机科学硕士</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>工商管理硕士 (MBA)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>数据科学与商业分析硕士</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>信息技术管理硕士</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">合作院校</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  APU 与英国多所知名大学合作，包括斯塔福德郡大学（Staffordshire University）等，提供双学位课程。学生可以获得 APU 和合作大学的双学位认证。
                </p>
              </div>
            </div>
          )}

          {activeTab === 'facilities' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">设施服务</h2>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">教学设施</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>现代化多媒体教室</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>专业计算机实验室</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>工程技术实验室</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>数字图书馆</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">生活设施</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>学生宿舍</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>餐厅与咖啡厅</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>运动场馆（篮球场、足球场、健身房）</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>医疗中心</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">学生服务</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>职业发展中心</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>学术咨询服务</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>国际学生支持</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>心理咨询服务</span>
                  </li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'activities' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">校园活动</h2>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">学术活动</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>学术研讨会与讲座</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>科技创新竞赛</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>黑客马拉松</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>商业案例分析大赛</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">文体活动</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>篮球、足球等体育比赛</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>音乐会与艺术展览</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>文化节与国际日</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>社团嘉年华</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">社团组织</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>学生会</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>技术社团（编程、机器人、AI）</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>体育社团（篮球社、足球社、羽毛球社）</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>艺术社团（音乐社、舞蹈社、摄影社）</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>志愿者组织</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * AI Assistant Types
 * 学脉AI助手相关类型定义
 */

export type AICategoryId = 'academic' | 'career' | 'startup' | 'writing' | 'tools'

export interface AIFunction {
  id: string
  name: string
  description: string
  icon: string
}

export interface AICategory {
  id: AICategoryId
  name: string
  icon: string
  color: string
  functions: AIFunction[]
}

export interface ConversationHistory {
  id: string
  title: string
  timestamp: string
  category: AICategoryId
}

// AI 功能分类数据
export const aiCategories: AICategory[] = [
  {
    id: 'academic',
    name: '学业助手',
    icon: '📚',
    color: 'bg-blue-500',
    functions: [
      {
        id: 'course-info',
        name: '课程信息查询',
        description: '快速查找课程信息、教学大纲、课程要求',
        icon: '📖',
      },
      {
        id: 'study-plan',
        name: '学业规划建议',
        description: '制定个性化的学业发展路径',
        icon: '🎯',
      },
      {
        id: 'study-methods',
        name: '学习方法建议',
        description: '获取高效的学习策略和技巧',
        icon: '💡',
      },
      {
        id: 'exam-prep',
        name: '考试复习计划',
        description: '定制科学的考试复习时间表',
        icon: '📝',
      },
    ],
  },
  {
    id: 'career',
    name: '职业发展',
    icon: '💼',
    color: 'bg-green-500',
    functions: [
      {
        id: 'resume-optimize',
        name: '简历优化',
        description: '专业的简历修改和优化建议',
        icon: '📄',
      },
      {
        id: 'mock-interview',
        name: '模拟面试',
        description: 'AI 驱动的面试模拟和反馈',
        icon: '🎤',
      },
      {
        id: 'career-planning',
        name: '职业规划',
        description: '个性化的职业发展路径建议',
        icon: '🚀',
      },
      {
        id: 'skill-improve',
        name: '技能提升建议',
        description: '针对性的技能发展方向指导',
        icon: '⚡',
      },
    ],
  },
  {
    id: 'startup',
    name: '创业助手',
    icon: '🚀',
    color: 'bg-purple-500',
    functions: [
      {
        id: 'business-plan',
        name: '商业计划书',
        description: '生成专业的商业计划书框架',
        icon: '📊',
      },
      {
        id: 'idea-validation',
        name: '创意验证',
        description: '评估商业创意的可行性',
        icon: '💭',
      },
      {
        id: 'market-analysis',
        name: '市场分析',
        description: '深入的市场研究和竞争分析',
        icon: '📈',
      },
      {
        id: 'funding-advice',
        name: '融资建议',
        description: '融资策略和投资人沟通指导',
        icon: '💰',
      },
    ],
  },
  {
    id: 'writing',
    name: '学术写作',
    icon: '✍️',
    color: 'bg-orange-500',
    functions: [
      {
        id: 'paper-polish',
        name: '论文润色',
        description: '提升学术论文的语言质量',
        icon: '✨',
      },
      {
        id: 'format-check',
        name: '格式检查',
        description: '确保论文符合规范格式',
        icon: '📐',
      },
      {
        id: 'citation-guide',
        name: '引用规范',
        description: 'APA、MLA 等引用格式指导',
        icon: '📚',
      },
      {
        id: 'grammar-check',
        name: '语法检查',
        description: '智能语法和拼写检查',
        icon: '✔️',
      },
    ],
  },
  {
    id: 'tools',
    name: '其他工具',
    icon: '🔧',
    color: 'bg-red-500',
    functions: [
      {
        id: 'info-analysis',
        name: '解读情报',
        description: '分析和解读复杂信息',
        icon: '🔍',
      },
      {
        id: 'industry-analysis',
        name: '行业分析',
        description: '深入了解行业动态和趋势',
        icon: '🏢',
      },
      {
        id: 'data-viz',
        name: '数据可视化',
        description: '将数据转化为可视化图表',
        icon: '📊',
      },
      {
        id: 'trend-forecast',
        name: '趋势预测',
        description: '基于数据的趋势预测分析',
        icon: '🔮',
      },
    ],
  },
]

// 模拟对话历史数据
export const mockConversationHistory: ConversationHistory[] = [
  {
    id: '1',
    title: 'AI学习路径规划',
    timestamp: '2小时前',
    category: 'academic',
  },
  {
    id: '2',
    title: '简历优化建议',
    timestamp: '1天前',
    category: 'career',
  },
  {
    id: '3',
    title: '模拟面试练习',
    timestamp: '2天前',
    category: 'career',
  },
  {
    id: '4',
    title: '商业计划书撰写',
    timestamp: '3天前',
    category: 'startup',
  },
  {
    id: '5',
    title: '论文语法检查',
    timestamp: '5天前',
    category: 'writing',
  },
]

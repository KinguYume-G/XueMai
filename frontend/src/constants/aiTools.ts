import { BookOpen, HelpCircle, PenTool, Lightbulb, FileText, Mic, Target, Zap, BarChart, Gem, TrendingUp, Search, Sparkles, FileCheck, SearchCheck, FileEdit, FileCode, DollarSign, Building, CheckSquare, MessageCircle } from 'lucide-react'

export interface AIFunction {
    id: string
    name: string
    category: string
    icon: any
    description: string
    route: string
}

export interface AICategory {
    id: string
    name: string
    icon: string
}

export const AI_CATEGORIES: AICategory[] = [
    { id: 'academic', name: '学业助手', icon: '📚' },
    { id: 'career', name: '职业发展', icon: '💼' },
    { id: 'startup', name: '创业助手', icon: '🚀' },
    { id: 'writing', name: '学术写作', icon: '✍️' },
    { id: 'tools', name: '其他工具', icon: '🔧' },
]

export const AI_FUNCTIONS: AIFunction[] = [
    // 通用对话
    {
        id: 'general',
        name: '智能对话',
        category: 'academic', // Default category
        icon: MessageCircle,
        description: '与AI进行自然流畅的对话',
        route: '/ai-chat/general'
    },

    // 学业助手 (4)
    {
        id: 'course_query',
        name: '课程查询',
        category: 'academic',
        icon: BookOpen,
        description: '查询课程信息、课表、学分要求',
        route: '/ai-chat/course_query'
    },
    {
        id: 'academic_qa',
        name: '学业问答',
        category: 'academic',
        icon: HelpCircle,
        description: '基于APU知识库回答学业问题',
        route: '/ai-chat/academic_qa'
    },
    {
        id: 'exam_prep',
        name: '考试准备',
        category: 'academic',
        icon: PenTool,
        description: '提供题库工具和考试策略',
        route: '/ai-chat/exam_prep'
    },
    {
        id: 'study_method',
        name: '学习方法',
        category: 'academic',
        icon: Lightbulb,
        description: '个性化学习方法建议',
        route: '/ai-chat/study_method'
    },

    // 职业发展 (4)
    {
        id: 'resume_optimize',
        name: '简历优化',
        category: 'career',
        icon: FileText,
        description: 'AI分析简历并提供优化建议',
        route: '/ai-chat/resume_optimize'
    },
    {
        id: 'mock_interview',
        name: '模拟面试',
        category: 'career',
        icon: Mic,
        description: '生成面试问题并评估回答',
        route: '/ai-chat/mock_interview'
    },
    {
        id: 'career_planning',
        name: '职业规划',
        category: 'career',
        icon: Target,
        description: '基于专业分析职业路径',
        route: '/ai-chat/career_planning'
    },
    {
        id: 'skill_upgrade',
        name: '技能提升',
        category: 'career',
        icon: Zap,
        description: '分析技能差距并推荐课程',
        route: '/ai-chat/skill_upgrade'
    },

    // 创业助手 (4)
    {
        id: 'business_plan',
        name: '商业计划',
        category: 'startup',
        icon: BarChart,
        description: '生成结构化商业计划书框架',
        route: '/ai-chat/business_plan'
    },
    {
        id: 'idea_validation',
        name: '创意验证',
        category: 'startup',
        icon: Gem,
        description: '评估商业创意可行性',
        route: '/ai-chat/idea_validation'
    },
    {
        id: 'market_analysis',
        name: '市场分析',
        category: 'startup',
        icon: TrendingUp,
        description: '分析行业趋势和竞争格局',
        route: '/ai-chat/market_analysis'
    },
    {
        id: 'competitor_analysis',
        name: '竞品分析',
        category: 'startup',
        icon: Search,
        description: '深入分析竞争对手策略',
        route: '/ai-chat/competitor_analysis'
    },

    // 学术写作 (4)
    {
        id: 'paper_polish',
        name: '论文润色',
        category: 'writing',
        icon: Sparkles,
        description: '提升学术论文语言质量',
        route: '/ai-chat/paper_polish'
    },
    {
        id: 'citation_format',
        name: '引用规范',
        category: 'writing',
        icon: FileCheck,
        description: 'APA/MLA等引用格式检查',
        route: '/ai-chat/citation_format'
    },
    {
        id: 'plagiarism_check',
        name: '查重检查',
        category: 'writing',
        icon: SearchCheck,
        description: '检测论文原创性',
        route: '/ai-chat/plagiarism_check'
    },
    {
        id: 'report_generate',
        name: '报告生成',
        category: 'writing',
        icon: FileEdit,
        description: '自动生成实验报告框架',
        route: '/ai-chat/report_generate'
    },

    // 其他工具 (4)
    {
        id: 'contract_template',
        name: '合同模板',
        category: 'tools',
        icon: FileCode,
        description: '生成常用合同模板',
        route: '/ai-chat/contract_template'
    },
    {
        id: 'salary_query',
        name: '薪资查询',
        category: 'tools',
        icon: DollarSign,
        description: 'Salary查询与对比分析',
        route: '/ai-chat/salary_query'
    },
    {
        id: 'company_review',
        name: '企业评价',
        category: 'tools',
        icon: Building,
        description: '分析公司背景与评价',
        route: '/ai-chat/company_review'
    },
    {
        id: 'grammar_check',
        name: '语法检查',
        category: 'tools',
        icon: CheckSquare,
        description: '多语言语法检查工具',
        route: '/ai-chat/grammar_check'
    }
]

export const getFunctionsByCategory = (categoryId: string) => {
    return AI_FUNCTIONS.filter(func =>
        func.category === categoryId && func.id !== 'general'  // Exclude general from category display
    )
}

export const getFunctionById = (functionId: string) => {
    return AI_FUNCTIONS.find(func => func.id === functionId)
}

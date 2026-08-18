import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageSquare, Trash2, Loader2 } from 'lucide-react'
import AIChatInput from '@/components/ai/AIChatInput'
import AIWelcome from '@/components/ai/AIWelcome'
import { AI_CATEGORIES, getFunctionsByCategory, getFunctionById } from '@/constants/aiTools'
import { conversationsApi, type Conversation } from '@/services/api/conversations'

export default function AITools() {
    const [activeCategory, setActiveCategory] = useState<string | null>(null)
    const [conversations, setConversations] = useState<Conversation[]>([])
    const [loadingConversations, setLoadingConversations] = useState(true)
    const [deletingId, setDeletingId] = useState<number | null>(null)
    const navigate = useNavigate()

    const currentCategory = activeCategory ? AI_CATEGORIES.find(c => c.id === activeCategory) : null
    const currentFunctions = activeCategory ? getFunctionsByCategory(activeCategory) : []

    // 加载对话历史
    useEffect(() => {
        loadConversations()
    }, [])

    const loadConversations = async () => {
        try {
            setLoadingConversations(true)
            const response = await conversationsApi.getConversations()
            setConversations(response.conversations || [])
        } catch (error) {
            console.error('加载对话历史失败:', error)
        } finally {
            setLoadingConversations(false)
        }
    }

    const handleDeleteConversation = async (id: number, e: React.MouseEvent) => {
        e.stopPropagation()
        
        if (!confirm('确定要删除这个对话吗？')) {
            return
        }

        try {
            setDeletingId(id)
            await conversationsApi.deleteConversation(id)
            setConversations(prev => prev.filter(c => c.id !== id))
        } catch (error) {
            console.error('删除对话失败:', error)
            alert('删除失败，请重试')
        } finally {
            setDeletingId(null)
        }
    }

    const formatTimestamp = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        const diffDays = Math.floor(diffMs / 86400000)

        if (diffMins < 1) return '刚刚'
        if (diffMins < 60) return `${diffMins}分钟前`
        if (diffHours < 24) return `${diffHours}小时前`
        if (diffDays === 1) return '昨天'
        if (diffDays < 7) return `${diffDays}天前`
        return date.toLocaleDateString('zh-CN')
    }

    const getFunctionIcon = (functionId: string) => {
        const iconMap: Record<string, string> = {
            'course_query': '📚',
            'academic_qa': '❓',
            'exam_prep': '📝',
            'study_method': '💡',
            'resume_optimize': '💼',
            'mock_interview': '🎤',
            'career_planning': '🎯',
            'skill_upgrade': '⚡',
            'business_plan': '🚀',
            'idea_validation': '💎',
            'market_analysis': '📈',
            'competitor_analysis': '🔍',
            'paper_polish': '✨',
            'citation_format': '📐',
            'plagiarism_check': '🔎',
            'report_generate': '📄',
            'contract_template': '📋',
            'salary_query': '💰',
            'company_review': '🏢',
            'grammar_check': '✅',
            'general': '💬',
        }
        return iconMap[functionId] || '💬'
    }

    const handleSendMessage = (message: string) => {
        if (message.trim()) {
            // Default to general chat if typing in the main box
            navigate(`/ai-chat/general?message=${encodeURIComponent(message.trim())}`)
        }
    }

    return (
        <div className="flex gap-6 h-[calc(100vh-8rem)] relative">
            {/* Left Sidebar - Categories & History */}
            <aside className="w-72 flex-shrink-0 overflow-y-auto space-y-4">
                {/* Categories */}
                <Card className="rounded-xl border shadow-sm">
                    <CardHeader className="pb-3 px-4 pt-4">
                        <CardTitle className="text-base font-semibold">AI 功能分类</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-1 px-2 pb-2">
                        {AI_CATEGORIES.map((category) => (
                            <Button
                                key={category.id}
                                variant={activeCategory === category.id ? 'secondary' : 'ghost'}
                                className={`w-full justify-start gap-3 h-11 px-4 ${activeCategory === category.id ? 'bg-secondary font-medium' : ''
                                    }`}
                                onClick={() => setActiveCategory(category.id)}
                            >
                                <span className="text-xl">{category.icon}</span>
                                <span>{category.name}</span>
                            </Button>
                        ))}
                    </CardContent>
                </Card>

                {/* History */}
                <Card className="rounded-xl border shadow-sm">
                    <CardHeader className="pb-3 px-4 pt-4">
                        <CardTitle className="flex items-center justify-between text-base font-semibold">
                            <div className="flex items-center gap-2">
                                <MessageSquare className="h-5 w-5 text-primary" />
                                对话历史
                            </div>
                            {conversations.length > 0 && (
                                <span className="text-xs font-normal text-muted-foreground">
                                    {conversations.length}个
                                </span>
                            )}
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-1 px-2 pb-2">
                        {loadingConversations ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                            </div>
                        ) : conversations.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
                                <div className="text-4xl mb-3">📭</div>
                                <p className="text-sm text-muted-foreground mb-1">暂无对话</p>
                                <p className="text-xs text-muted-foreground">点击右侧功能卡片开始吧 →</p>
                            </div>
                        ) : (
                            conversations.map((conversation) => {
                                const func = getFunctionById(conversation.ai_function)
                                return (
                                    <div
                                        key={conversation.id}
                                        className="group flex w-full items-center gap-2 rounded-lg px-3 py-3 text-sm transition-colors hover:bg-secondary/80 cursor-pointer text-left relative"
                                        onClick={() => navigate(`/ai-chat/${conversation.ai_function}?conversation_id=${conversation.id}`)}
                                    >
                                        <span className="text-lg flex-shrink-0">
                                            {getFunctionIcon(conversation.ai_function)}
                                        </span>
                                        <div className="flex-1 min-w-0">
                                            <div className="font-medium text-foreground line-clamp-1">
                                                {conversation.title || func?.name || '未命名对话'}
                                            </div>
                                            <div className="text-xs text-muted-foreground flex items-center gap-2">
                                                <span>{formatTimestamp(conversation.updated_at)}</span>
                                                <span>·</span>
                                                <span>{conversation.message_count}条消息</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => handleDeleteConversation(conversation.id, e)}
                                            disabled={deletingId === conversation.id}
                                            className="flex-shrink-0 opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                                            title="删除对话"
                                        >
                                            {deletingId === conversation.id ? (
                                                <Loader2 className="h-4 w-4 animate-spin text-red-500" />
                                            ) : (
                                                <Trash2 className="h-4 w-4 text-red-500" />
                                            )}
                                        </button>
                                    </div>
                                )
                            })
                        )}
                    </CardContent>
                </Card>
            </aside>

            {/* Center Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto pb-6">
                    <Card className="min-h-full rounded-xl border shadow-sm p-6">
                        {!currentCategory ? (
                            <AIWelcome />
                        ) : (
                            <div className="space-y-6">
                                {/* Category Header */}
                                <div className="flex items-center gap-3 pb-4 border-b">
                                    <span className="text-4xl">{currentCategory?.icon}</span>
                                    <div>
                                        <h2 className="text-2xl font-bold text-foreground">
                                            {currentCategory?.name}
                                        </h2>
                                        <p className="text-sm text-muted-foreground mt-1">
                                            选择下方功能开始使用
                                        </p>
                                    </div>
                                </div>

                                {/* Function Cards Grid */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {currentFunctions.map((func) => {
                                        const Icon = func.icon
                                        return (
                                            <Card
                                                key={func.id}
                                                className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-primary/50 group"
                                                onClick={() => navigate(func.route)}
                                            >
                                                <CardContent className="p-6">
                                                    <div className="flex flex-col items-center text-center space-y-3">
                                                        {/* Icon */}
                                                        <div className="text-4xl group-hover:scale-110 transition-transform duration-200 text-primary">
                                                            <Icon className="w-8 h-8" />
                                                        </div>

                                                        {/* Name */}
                                                        <h3 className="font-semibold text-base text-foreground group-hover:text-primary transition-colors">
                                                            {func.name}
                                                        </h3>

                                                        {/* Description */}
                                                        <p className="text-sm text-muted-foreground line-clamp-2">
                                                            {func.description}
                                                        </p>
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        )
                                    })}
                                </div>
                            </div>
                        )}
                    </Card>
                </div>

                {/* Chat Input */}
                <div className="flex-shrink-0 mt-4">
                    <AIChatInput onSend={handleSendMessage} />
                </div>
            </main>
        </div>
    )
}

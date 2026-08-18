/**
 * AI 主页侧边栏组件
 * 显示在主页左侧或右侧，展示对话历史列表
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageSquare, Trash2, Loader2, Plus } from 'lucide-react'
import { conversationsApi, type Conversation } from '@/services/api/conversations'
import { toast } from '@/store/useToastStore'

export default function AIHomeSidebar() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loadingConversations, setLoadingConversations] = useState(true)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const navigate = useNavigate()

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
      toast.error('加载对话历史失败')
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
      toast.success('对话已删除')
    } catch (error) {
      console.error('删除对话失败:', error)
      toast.error('删除失败，请重试')
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

  return (
    <Card className="rounded-xl border shadow-sm h-full flex flex-col">
      <CardHeader className="pb-3 px-4 pt-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base font-semibold">
            <MessageSquare className="h-5 w-5 text-primary" />
            对话历史
          </CardTitle>
          <div className="flex items-center gap-2">
            {conversations.length > 0 && (
              <span className="text-xs font-normal text-muted-foreground">
                {conversations.length}个
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              onClick={() => navigate('/ai-tools')}
              title="新建对话"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-1 px-2 pb-2 flex-1 overflow-y-auto">
        {loadingConversations ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <div className="text-5xl mb-4">💬</div>
            <p className="text-sm text-muted-foreground mb-2">暂无对话</p>
            <p className="text-xs text-muted-foreground mb-4">点击下方按钮开始AI对话</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/ai-tools')}
            >
              开始对话
            </Button>
          </div>
        ) : (
          conversations.map((conversation) => {
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
                  {/* ✅ 显示用户消息作为标题，而非功能ID */}
                  <div className="font-medium text-foreground line-clamp-1" title={conversation.title}>
                    {conversation.title}
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
  )
}



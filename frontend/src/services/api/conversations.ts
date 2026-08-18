import { apiClient } from '@/lib/api/client';

/**
 * 对话相关的API接口
 */

export interface Conversation {
  id: number;
  user: number;
  ai_function: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  total_tokens: number;
}

export interface ConversationMessage {
  id: number;
  conversation: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  metadata?: {
    routed_to?: string;
    confidence?: number;
    method?: string;
    used_rag?: boolean;
    model?: string;
    context_messages_count?: number;
    total_tokens?: number;
  };
}

export interface ConversationsListResponse {
  conversations: Conversation[];
  total: number;
}

export interface CreateConversationRequest {
  ai_function: string;
  title?: string;
}

export interface ChatRequest {
  question: string;
  mode?: string;
  use_rag?: boolean;
}

export interface ChatResponse {
  answer: string;
  routed_to: string;
  confidence: number;
  method: string;
  elapsed_ms: number;
  used_rag: boolean;
  model: string;
  context_messages_count?: number;
  total_tokens?: number;
}

export const conversationsApi = {
  /**
   * 获取对话列表
   */
  getConversations: async (): Promise<ConversationsListResponse> => {
    const response = await apiClient.get<ConversationsListResponse>('/ai/conversations/');
    return response;
  },

  /**
   * 创建新对话
   */
  createConversation: async (data: CreateConversationRequest): Promise<Conversation> => {
    const response = await apiClient.post<Conversation>('/ai/conversations/', data);
    return response;
  },

  /**
   * 获取对话详情（包含消息）
   */
  getConversation: async (id: number): Promise<Conversation> => {
    const response = await apiClient.get<{ conversation: Conversation }>(
      `/ai/conversations/${id}/`
    );
    return response.conversation;
  },

  /**
   * 删除对话
   */
  deleteConversation: async (id: number): Promise<void> => {
    await apiClient.delete(`/ai/conversations/${id}/`);
  },

  /**
   * 获取对话的消息列表
   */
  getMessages: async (conversationId: number): Promise<ConversationMessage[]> => {
    const response = await apiClient.get<{ messages: ConversationMessage[] }>(
      `/ai/conversations/${conversationId}/messages/`
    );
    return response.messages;
  },

  /**
   * 发送消息到指定对话（非流式）
   */
  sendMessage: async (conversationId: number, data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>(
      `/ai/conversations/${conversationId}/chat/`,
      data
    );
    return response;
  },
};







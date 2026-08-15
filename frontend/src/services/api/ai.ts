import { apiClient } from '@/lib/api/client';

export interface AIQueryRequest {
  query: string;
  university_id?: number;
}

export interface AIQueryResponse {
  answer: string;
  used_rag: boolean;
  elapsed_ms?: number;
}

export const aiApi = {
  /**
   * AI查询（RAG）
   */
  query: async (data: AIQueryRequest): Promise<AIQueryResponse> => {
    return await apiClient.post<AIQueryResponse>('/ai/chat/sync/', {
      question: data.query,
      use_rag: true,
      university_id: data.university_id,
    }) as unknown as AIQueryResponse;
  },
};

import { apiClient } from '@/lib/api/client';

export interface AIQueryRequest {
  query: string;
  university_id?: number;
}

export interface AIQueryResponse {
  query: string;
  response: string;
  is_mock: boolean;
  matched_chunks?: number[];
}

export const aiApi = {
  /**
   * AI查询（RAG）
   */
  query: async (data: AIQueryRequest): Promise<AIQueryResponse> => {
    const result = await apiClient.post<{ answer: string; used_rag: boolean }>(
      '/ai/chat/sync/',
      { question: data.query, use_rag: true, university_id: data.university_id }
    );
    return {
      query: data.query,
      response: result.answer,
      is_mock: false,
    };
  },
};

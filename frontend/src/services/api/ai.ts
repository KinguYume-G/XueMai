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
    const response = await apiClient.post<{ data: AIQueryResponse }>('/ai/query/', data);
    return (response as { data: AIQueryResponse }).data;
  },
};


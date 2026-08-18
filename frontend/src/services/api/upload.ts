import { apiClient, apiFetch, readApiErrorMessage } from '@/lib/api/client'

/**
 * 文件上传API
 */

export interface UploadFileResponse {
  document_id: number
  file_name: string
  file_type: string
  file_size: number
  extracted_text_length: number
  extracted_text_preview: string
  preview_url: string
}

export interface AnalyzeDocumentResponse {
  analysis: string
  task: string
  document_title: string
  elapsed_ms: number
}

/**
 * 上传文件
 */
export const uploadFile = async (file: File, conversationId?: number): Promise<UploadFileResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  if (conversationId) {
    formData.append('conversation_id', conversationId.toString())
  }

  const response = await apiFetch('/ai/upload/', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(await readApiErrorMessage(response, '文件上传失败'))
  }

  const payload = await response.json() as UploadFileResponse | { data: UploadFileResponse }
  return 'data' in payload ? payload.data : payload
}

/**
 * 分析文档
 */
export const analyzeDocument = async (
  documentId: number,
  task: string = 'summarize',
  instructions?: string
): Promise<AnalyzeDocumentResponse> => {
  return apiClient.post(`/ai/documents/${documentId}/analyze/`, {
    task,
    instructions,
  })
}

/**
 * 删除文档
 */
export const deleteDocument = async (documentId: number): Promise<void> => {
  await apiClient.delete(`/ai/documents/${documentId}/`)
}




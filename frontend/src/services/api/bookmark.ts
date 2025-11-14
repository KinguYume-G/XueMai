import { apiClient } from '@/lib/api/client'

export interface Bookmark {
  id: number
  content_type: 'post' | 'exchange' | 'internship' | 'community'
  object_id: number
  created_at: string
  item: any  // 关联对象的详细信息
}

export async function listBookmarks(type?: string) {
  console.log('📡 [API] 调用 listBookmarks, type:', type)
  const params = type ? { type } : {}
  // apiClient 的响应拦截器已经提取了数据，所以 data 就是数组本身
  const data = await apiClient.get<Bookmark[]>('/bookmarks/', { params })
  console.log('✅ [API] listBookmarks 响应数据:', data)
  console.log('✅ [API] 数据类型:', Array.isArray(data) ? 'array' : typeof data)
  // 包装成对象以匹配 Store 的期望 (response.data)
  return { data }
}

export async function toggleBookmark(content_type: string, object_id: number) {
  return apiClient.post('/bookmarks/toggle/', { content_type, object_id })
}

export async function deleteBookmark(id: number) {
  return apiClient.delete(`/bookmarks/${id}/`)
}

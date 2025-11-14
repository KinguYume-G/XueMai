import { create } from 'zustand'
import { listBookmarks, toggleBookmark, deleteBookmark, type Bookmark } from '@/services/api/bookmark'

// 初始状态确保 bookmarks 始终是数组
const INITIAL_STATE = {
  bookmarks: [] as Bookmark[],
  loading: false,
  error: null as string | null,
}

interface BookmarkState {
  bookmarks: Bookmark[]
  loading: boolean
  error: string | null

  fetchBookmarks: (type?: string) => Promise<void>
  toggleBookmark: (content_type: string, object_id: number) => Promise<void>
  removeBookmark: (id: number) => Promise<void>
}

export const useBookmarkStore = create<BookmarkState>((set, get) => ({
  ...INITIAL_STATE,

  fetchBookmarks: async (type?: string) => {
    console.log('🔄 [Store] fetchBookmarks 开始, type:', type)
    set({ loading: true, error: null })

    try {
      console.log('📡 [Store] 准备调用 API')
      const response = await listBookmarks(type)
      console.log('✅ [Store] API 响应:', response)
      console.log('✅ [Store] response.data:', response?.data)
      console.log('✅ [Store] response.data 类型:', Array.isArray(response?.data) ? 'array' : typeof response?.data)

      // 防御性检查：确保返回的是数组
      const rawData = response?.data ?? []
      const bookmarks = Array.isArray(rawData) ? rawData : []
      console.log('📦 [Store] 最终 bookmarks:', bookmarks.length, '个')

      if (bookmarks.length > 0) {
        console.log('📦 [Store] 第一个收藏:', bookmarks[0])
      }

      set({ bookmarks, loading: false })
    } catch (error: any) {
      console.error('❌ [Store] 错误:', error)
      // 错误时也要保持 bookmarks 为空数组
      set({ error: error.message, bookmarks: [], loading: false })
    }
  },

  toggleBookmark: async (content_type: string, object_id: number) => {
    try {
      await toggleBookmark(content_type, object_id)
      // Refresh bookmarks
      await get().fetchBookmarks()
    } catch (error: any) {
      console.error('Toggle bookmark error:', error)
    }
  },

  removeBookmark: async (id: number) => {
    try {
      await deleteBookmark(id)
      // Remove from local state immediately
      set((state) => ({
        bookmarks: state.bookmarks.filter(b => b.id !== id)
      }))
    } catch (error: any) {
      console.error('Remove bookmark error:', error)
    }
  }
}))

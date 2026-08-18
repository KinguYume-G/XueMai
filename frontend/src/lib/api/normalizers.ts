import type { Post, PostApiRecord } from '@/types/api'

export const normalizePost = (post: PostApiRecord): Post => ({
  id: post.id,
  author: post.author.id,
  author_username: post.author.username,
  title: post.title ?? '',
  body: post.body,
  image_url: post.image_url,
  visibility: post.visibility,
  is_published: post.is_published,
  target_university: post.target_university,
  target_school: post.target_school,
  tags: post.tags.map((tag) => tag.id),
  tags_data: post.tags,
  likes_count: post.likes_count,
  comments_count: post.comments_count,
  bookmarks_count: post.bookmarks_count,
  views_count: post.views_count,
  is_liked: post.is_liked,
  is_bookmarked: post.is_bookmarked,
  created_at: post.created_at,
  updated_at: post.updated_at,
})

export interface User {
  id: string
  name: string
  avatar: string
  school: string
  schoolBadge?: string
}

export interface Post {
  id: string
  author: User
  timestamp: string
  title: string
  content: string
  image?: string
  tags?: string[]
  likes: number
  comments: number
  shares: number
  isLiked: boolean
}

export interface School {
  id: string
  name: string
  isLocked: boolean
}

export interface Topic {
  id: string
  title: string
  tag: string
}

export interface ExchangeProgram {
  id: string
  title: string
  deadline: string
}


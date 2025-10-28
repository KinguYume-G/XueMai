import { Post, School, Topic, ExchangeProgram } from '@/types/post'

export const mockPosts: Post[] = [
  {
    id: '1',
    author: {
      id: 'user1',
      name: 'Jane Doe',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jane',
      school: 'APU',
      schoolBadge: '🎓'
    },
    timestamp: '2小时前 · #极端生活',
    title: '成为下一个大型科创新者',
    content: '在亚太科技大学（APU），我们不仅仅是教育学生。我们还培养能够塑造未来的创新者、领导者和思想家。释放您的潜力，成为一名技术大师。',
    image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop',
    likes: 122,
    comments: 15,
    shares: 8,
    isLiked: false
  },
  {
    id: '2',
    author: {
      id: 'user2',
      name: 'John Smith',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
      school: 'APU',
      schoolBadge: '🎓'
    },
    timestamp: '5小时前 · #招聘',
    title: '招聘前端开发实习生！',
    content: '我们的创业团队正在寻找一名充满激情的前端开发实习生。参与我们的 AI 教育平台项目。要求熟悉 React 和 Tailwind CSS。这是一个住在学习和成长机会！感兴趣的同学请私信。',
    tags: ['React', 'Tailwind CSS', '实习'],
    likes: 89,
    comments: 23,
    shares: 5,
    isLiked: false
  }
]

export const mockSchools: School[] = [
  { id: 'apu', name: 'APU 专区', isLocked: false },
  { id: 'tsinghua', name: '清华大学专区', isLocked: true },
  { id: 'pku', name: '北京大学专区', isLocked: true }
]

export const mockTopics: Topic[] = [
  { id: '1', title: 'AI论文写作技巧', tag: '#AI论文写作技巧' },
  { id: '2', title: '马来西亚实习机指南', tag: '#马来西亚实习机指南' },
  { id: '3', title: '跨文化交流经验', tag: '#跨文化交流经验' },
  { id: '4', title: '2024秋季交换信息', tag: '#2024秋季交换信息' }
]

export const mockExchangePrograms: ExchangeProgram[] = [
  {
    id: '1',
    title: '新加坡国立大学交换',
    deadline: '截止日期: 2024-10-15'
  },
  {
    id: '2',
    title: '香港大学暑期项目',
    deadline: '截止日期: 2024-11-01'
  }
]

export const getPosts = async (): Promise<Post[]> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockPosts), 300)
  })
}

export const getSchools = async (): Promise<School[]> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockSchools), 200)
  })
}

export const getTopics = async (): Promise<Topic[]> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockTopics), 200)
  })
}

export const getExchangePrograms = async (): Promise<ExchangeProgram[]> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockExchangePrograms), 200)
  })
}


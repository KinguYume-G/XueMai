import { useState } from 'react'
import { Image, Video, Link as LinkIcon, Hash } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'

export default function CreatePostBox() {
  const [content, setContent] = useState('')

  return (
    <Card className="border shadow-sm">
      <div className="p-4">
        <div className="flex gap-3">
          <Avatar className="h-10 w-10">
            <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=User" />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          
          <div className="flex-1">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="分享你的想法...（荣助/经验/招聘/作品）"
              className="w-full resize-none border-0 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-0 min-h-[60px]"
            />
            
            <div className="flex items-center justify-between mt-3 pt-3 border-t">
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label="添加图片"
                >
                  <Image className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label="添加视频"
                >
                  <Video className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label="添加链接"
                >
                  <LinkIcon className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground hover:text-primary"
                  aria-label="添加话题"
                >
                  <Hash className="h-5 w-5" />
                </Button>
              </div>
              
              <Button
                disabled={!content.trim()}
                className="rounded-full px-6 h-9 bg-primary hover:bg-primary/90"
              >
                发布
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}


import { useState, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, Video, Image as ImageIcon, FileText, Loader2, X } from 'lucide-react'
import { uploadFile, type UploadFileResponse } from '@/services/api/upload'
import { toast } from '@/store/useToastStore'

interface AIChatInputProps {
  onSend?: (message: string) => void
}

/**
 * AI 聊天输入框组件
 * 底部固定的聊天输入区域，包含输入框、附件按钮和发送按钮
 */
export default function AIChatInput({ onSend }: AIChatInputProps) {
  const { t } = useTranslation()
  const [message, setMessage] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<UploadFileResponse[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSend = () => {
    if (message.trim()) {
      console.log('发送消息:', message)
      if (onSend) {
        // 如果有上传的文件，附加文件信息
        let messageWithFiles = message
        if (uploadedFiles.length > 0) {
          const fileInfo = uploadedFiles.map(f => t('aiChat.input.uploadedFileAttachment', { name: f.file_name })).join('\n')
          messageWithFiles = `${message}\n\n${fileInfo}`
        }
        onSend(messageWithFiles)
      }
      setMessage('')
      setUploadedFiles([]) // 清空已上传文件
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 处理文件选择
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return
    
    const file = files[0]
    
    // 验证文件大小（10MB限制）
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      toast.error(t('aiChat.input.fileTooLarge'))
      return
    }
    
    // 开始上传
    setUploading(true)
    setUploadProgress(0)
    
    try {
      // 模拟进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)
      
      const result = await uploadFile(file)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      // 添加到已上传文件列表
      setUploadedFiles(prev => [...prev, result])
      
      toast.success(t('aiChat.input.fileUploadSuccess', { name: result.file_name }))

      // 自动建议分析
      setTimeout(() => {
        setMessage(t('aiChat.input.analyzeFilePrompt', { type: result.file_type }))
      }, 500)

    } catch (error: unknown) {
      console.error('文件上传失败:', error)
      const errorMessage = error instanceof Error ? error.message : t('aiChat.input.fileUploadFailed')
      toast.error(errorMessage)
    } finally {
      setUploading(false)
      setUploadProgress(0)
      // 清空input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }
  
  // 删除已上传文件
  const handleRemoveFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
    toast.success(t('aiChat.input.fileRemoved'))
  }

  const handleFileUpload = (type: 'video' | 'image' | 'document') => {
    if (!fileInputRef.current) return
    
    // 设置接受的文件类型
    const acceptMap = {
      video: '.mp4,.mov,.avi',
      image: '.jpg,.jpeg,.png,.gif',
      document: '.pdf,.docx,.doc,.txt,.csv'
    }
    
    fileInputRef.current.accept = acceptMap[type]
    fileInputRef.current.click()
  }

  return (
    <Card className="sticky bottom-0 left-0 right-0 bg-white border-t shadow-lg rounded-none">
      <div className="p-4">
        {/* 已上传文件列表 */}
        {uploadedFiles.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg text-sm"
              >
                <FileText className="h-4 w-4 text-blue-600" />
                <span className="text-blue-900 font-medium">{file.file_name}</span>
                <span className="text-blue-600 text-xs">
                  ({(file.file_size / 1024).toFixed(1)}KB)
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(index)}
                  className="ml-1 p-0.5 hover:bg-blue-200 rounded transition-colors"
                  title={t('aiChat.input.removeFileTitle')}
                >
                  <X className="h-3 w-3 text-blue-700" />
                </button>
              </div>
            ))}
          </div>
        )}
        
        {/* 上传进度条 */}
        {uploading && (
          <div className="mb-3 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
              <span>{t('aiChat.input.uploading')}</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}
        
        {/* 隐藏的文件输入 */}
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileSelect}
        />
        
        <div className="flex items-end gap-3">
          {/* 附件按钮组 */}
          <div className="flex gap-2">
            {/* 视频上传 */}
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 rounded-full"
              onClick={() => handleFileUpload('video')}
              title={t('aiChat.input.uploadVideoTitle')}
              disabled={uploading}
            >
              {uploading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Video className="h-5 w-5" />}
            </Button>

            {/* 图片上传 */}
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 rounded-full"
              onClick={() => handleFileUpload('image')}
              title={t('aiChat.input.uploadImageTitle')}
              disabled={uploading}
            >
              {uploading ? <Loader2 className="h-5 w-5 animate-spin" /> : <ImageIcon className="h-5 w-5" />}
            </Button>

            {/* 文档上传 */}
            <Button
              variant="outline"
              size="icon"
              className="h-10 w-10 rounded-full"
              onClick={() => handleFileUpload('document')}
              title={t('aiChat.input.uploadDocumentTitle')}
              disabled={uploading}
            >
              {uploading ? <Loader2 className="h-5 w-5 animate-spin" /> : <FileText className="h-5 w-5" />}
            </Button>
          </div>

          {/* 输入框 */}
          <div className="flex-1">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('aiChat.input.placeholder')}
              className="h-10 resize-none border-2 focus:border-primary"
            />
          </div>

          {/* 发送按钮 */}
          <Button
            onClick={handleSend}
            disabled={!message.trim()}
            className="h-10 w-10 rounded-full p-0"
            size="icon"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>

        {/* 提示文字 */}
        <div className="mt-2 text-xs text-muted-foreground text-center">
          {t('aiChat.input.disclaimer')}
        </div>
      </div>
    </Card>
  )
}

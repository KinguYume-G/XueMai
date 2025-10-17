import React, { useState } from 'react';
import { Image, Link, BarChart } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { User } from 'lucide-react';

interface CreatePostBoxProps {
  onPost: (content: string, images: File[]) => void;
  userAvatar?: string;
  userName?: string;
}

const CreatePostBox: React.FC<CreatePostBoxProps> = ({
  onPost,
  userAvatar = '/placeholder-avatar.jpg',
  userName = '用户'
}) => {
  const [content, setContent] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [images, setImages] = useState<File[]>([]);

  const handleSubmit = () => {
    if (content.trim()) {
      onPost(content, images);
      setContent('');
      setImages([]);
      setIsFocused(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setImages(prev => [...prev, ...files]);
  };

  const removeImage = (index: number) => {
    setImages(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Card className="mb-6">
      <CardContent className="p-4">
        <div className="flex space-x-3">
          {/* User Avatar */}
          <Avatar className="h-10 w-10 flex-shrink-0">
            <AvatarImage src={userAvatar} alt={userName} />
            <AvatarFallback>
              <User className="h-4 w-4" />
            </AvatarFallback>
          </Avatar>

          {/* Content Area */}
          <div className="flex-1 space-y-3">
            {/* Text Input */}
            <div>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => {
                  if (!content.trim()) {
                    setIsFocused(false);
                  }
                }}
                placeholder="分享你的想法...（实时/经验/招聘/作品）"
                className="w-full resize-none border-0 focus:outline-none focus:ring-0 text-base placeholder-gray-500 min-h-[60px] max-h-[200px]"
                rows={isFocused ? 3 : 1}
              />
            </div>

            {/* Image Preview */}
            {images.length > 0 && (
              <div className="grid grid-cols-2 gap-2">
                {images.map((image, index) => (
                  <div key={index} className="relative">
                    <img
                      src={URL.createObjectURL(image)}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-24 object-cover rounded-lg"
                    />
                    <button
                      onClick={() => removeImage(index)}
                      className="absolute top-1 right-1 bg-black bg-opacity-50 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-opacity-70"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Action Bar */}
            {(isFocused || content.trim() || images.length > 0) && (
              <div className="flex items-center justify-between pt-2 border-t">
                <div className="flex items-center space-x-2">
                  {/* Image Upload */}
                  <label htmlFor="image-upload" className="cursor-pointer">
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <Image className="h-4 w-4" />
                    </Button>
                    <input
                      id="image-upload"
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                  </label>

                  {/* Link */}
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <Link className="h-4 w-4" />
                  </Button>

                  {/* Poll */}
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <BarChart className="h-4 w-4" />
                  </Button>
                </div>

                {/* Post Button */}
                <Button
                  onClick={handleSubmit}
                  disabled={!content.trim() && images.length === 0}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6"
                >
                  发帖
                </Button>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CreatePostBox;

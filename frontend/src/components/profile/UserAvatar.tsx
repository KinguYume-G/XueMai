import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { User } from 'lucide-react';

interface UserAvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  badge?: string;
  size?: 'sm' | 'md' | 'lg';
  showBadge?: boolean;
  className?: string;
}

const UserAvatar: React.FC<UserAvatarProps> = ({
  src,
  alt,
  name = '用户',
  badge,
  size = 'md',
  showBadge = false,
  className
}) => {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12'
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className={`relative inline-block ${className}`}>
      <Avatar className={sizeClasses[size]}>
        <AvatarImage src={src} alt={alt || name} />
        <AvatarFallback className="bg-blue-100 text-blue-700 font-semibold">
          {getInitials(name)}
        </AvatarFallback>
      </Avatar>
      
      {showBadge && badge && (
        <Badge 
          variant="secondary" 
          className="absolute -top-1 -right-1 text-xs px-1.5 py-0.5"
        >
          {badge}
        </Badge>
      )}
    </div>
  );
};

export default UserAvatar;

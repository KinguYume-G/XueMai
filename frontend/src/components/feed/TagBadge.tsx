import React from 'react';
import { cn } from '../../lib/utils';

interface TagBadgeProps {
  label: string;
  variant: 'blue' | 'green' | 'yellow' | 'gray';
  onClick?: () => void;
  className?: string;
}

const TagBadge: React.FC<TagBadgeProps> = ({ 
  label, 
  variant, 
  onClick, 
  className 
}) => {
  const variantStyles = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100',
    green: 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100',
    gray: 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100',
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border transition-all duration-200 hover:scale-105',
        variantStyles[variant],
        onClick && 'cursor-pointer',
        !onClick && 'cursor-default',
        className
      )}
    >
      {label}
    </button>
  );
};

export default TagBadge;

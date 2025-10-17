import React, { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';
import { Button } from '../ui/button';

interface LanguageSwitchProps {
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  onLanguageChange?: (language: string) => void;
}

const LanguageSwitch: React.FC<LanguageSwitchProps> = ({
  className,
  showLabel = true,
  size = 'md',
  onLanguageChange
}) => {
  const [currentLanguage, setCurrentLanguage] = useState('中文');

  const languages = [
    { code: 'zh', name: '中文', display: '中文' },
    { code: 'en', name: 'English', display: 'EN' }
  ];

  useEffect(() => {
    // 检查本地存储的语言设置
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage) {
      const lang = languages.find(l => l.code === savedLanguage);
      if (lang) {
        setCurrentLanguage(lang.name);
      }
    }
  }, []);

  const toggleLanguage = () => {
    const currentIndex = languages.findIndex(lang => lang.name === currentLanguage);
    const nextIndex = (currentIndex + 1) % languages.length;
    const nextLanguage = languages[nextIndex];
    
    setCurrentLanguage(nextLanguage.name);
    localStorage.setItem('language', nextLanguage.code);
    onLanguageChange?.(nextLanguage.code);
  };

  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12'
  };

  const iconSizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  };

  const getDisplayText = () => {
    const current = languages.find(lang => lang.name === currentLanguage);
    const next = languages.find(lang => lang.name !== currentLanguage);
    return `${current?.display} / ${next?.display}`;
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleLanguage}
      className={`${sizeClasses[size]} p-0 ${className}`}
      aria-label={`当前语言: ${currentLanguage}`}
    >
      <Globe className={`${iconSizes[size]} ${showLabel ? 'mr-2' : ''}`} />
      {showLabel && <span className="text-sm">{getDisplayText()}</span>}
    </Button>
  );
};

export default LanguageSwitch;

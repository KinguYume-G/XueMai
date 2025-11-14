import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zhTranslation from './locales/zh.json';
import enTranslation from './locales/en.json';

// 从 localStorage 获取保存的语言，如果没有则使用浏览器语言或默认中文
const getInitialLanguage = (): string => {
  const savedLanguage = localStorage.getItem('language');
  if (savedLanguage && ['zh', 'en'].includes(savedLanguage)) {
    return savedLanguage;
  }

  // 检测浏览器语言
  const browserLanguage = navigator.language.toLowerCase();
  if (browserLanguage.startsWith('zh')) {
    return 'zh';
  } else if (browserLanguage.startsWith('en')) {
    return 'en';
  }

  // 默认使用中文
  return 'zh';
};

i18n
  .use(initReactI18next) // 将 i18n 传递给 react-i18next
  .init({
    resources: {
      zh: {
        translation: zhTranslation,
      },
      en: {
        translation: enTranslation,
      },
    },
    lng: getInitialLanguage(), // 默认语言
    fallbackLng: 'zh', // 回退语言
    interpolation: {
      escapeValue: false, // React 已经默认转义
    },
    react: {
      useSuspense: false, // 禁用 Suspense 模式
    },
  });

export default i18n;

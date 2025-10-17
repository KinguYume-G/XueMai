import { useState, useEffect, useCallback } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role?: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  name: string;
  email: string;
  phone: string;
  password: string;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false
  });

  // 检查本地存储的认证状态
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (token) {
          // 这里应该验证token的有效性
          // 暂时模拟从token中获取用户信息
          const user = JSON.parse(localStorage.getItem('user') || 'null');
          if (user) {
            setAuthState({
              user,
              isLoading: false,
              isAuthenticated: true
            });
          } else {
            // Token存在但用户信息无效，清除认证状态
            logout();
          }
        } else {
          setAuthState({
            user: null,
            isLoading: false,
            isAuthenticated: false
          });
        }
      } catch (error) {
        console.error('Auth check error:', error);
        logout();
      }
    };

    checkAuthStatus();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      // 这里会调用实际的登录API
      // const response = await api.post('/auth/login', credentials);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模拟成功登录
      const user: User = {
        id: '1',
        name: '张小明',
        email: credentials.email,
        avatar: '/placeholder-avatar.jpg',
        role: 'student'
      };
      
      const token = 'mock-jwt-token';
      
      // 保存到本地存储
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      setAuthState({
        user,
        isLoading: false,
        isAuthenticated: true
      });
      
      return { success: true, user };
    } catch (error) {
      console.error('Login error:', error);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return { success: false, error: error.message };
    }
  }, []);

  const register = useCallback(async (userData: RegisterData) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      // 这里会调用实际的注册API
      // const response = await api.post('/auth/register', userData);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模拟成功注册
      const user: User = {
        id: '1',
        name: userData.name,
        email: userData.email,
        avatar: '/placeholder-avatar.jpg',
        role: 'student'
      };
      
      const token = 'mock-jwt-token';
      
      // 保存到本地存储
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      setAuthState({
        user,
        isLoading: false,
        isAuthenticated: true
      });
      
      return { success: true, user };
    } catch (error) {
      console.error('Register error:', error);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return { success: false, error: error.message };
    }
  }, []);

  const logout = useCallback(() => {
    // 清除本地存储
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    
    setAuthState({
      user: null,
      isLoading: false,
      isAuthenticated: false
    });
  }, []);

  const updateProfile = useCallback(async (profileData: Partial<User>) => {
    try {
      if (!authState.user) return { success: false, error: 'Not authenticated' };
      
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      // 这里会调用实际的更新用户信息API
      // const response = await api.put('/auth/profile', profileData);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 更新用户信息
      const updatedUser = { ...authState.user, ...profileData };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      setAuthState(prev => ({
        ...prev,
        user: updatedUser,
        isLoading: false
      }));
      
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error('Update profile error:', error);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      return { success: false, error: error.message };
    }
  }, [authState.user]);

  return {
    ...authState,
    login,
    register,
    logout,
    updateProfile
  };
};

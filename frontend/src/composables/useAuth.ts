import { ref } from 'vue';
import { useRouter } from 'vue-router';

// 从本地存储中获取初始认证状态


export function useAuth() {
  const router = useRouter();
  const isAuthenticated = ref(localStorage.getItem('isAuthenticated') === 'true');
  const login = async () => {
    try {
      isAuthenticated.value = true;
      localStorage.setItem('isAuthenticated', 'true');
      await router.push('/welcome');
    } catch (error) {
      console.error('Login navigation failed:', error);
      // 如果导航失败，清除认证状态
      isAuthenticated.value = false;
      localStorage.removeItem('isAuthenticated');
    }
  };

  const logout = async () => {
    try {
      isAuthenticated.value = false;
      localStorage.removeItem('isAuthenticated');
      await router.push('/signin'); // 确保导航到登录页面
    } catch (error) {
      console.error('Logout navigation failed:', error);
    }
  };

  const checkAuth = () => {
    return localStorage.getItem('isAuthenticated') === 'true';
  };

  return {
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };
}

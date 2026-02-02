import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '');
  const user = ref(null);

  function setToken(newToken) {
    token.value = newToken;
    localStorage.setItem('token', newToken);
  }

  function setUser(newUser) {
    user.value = newUser;
  }

  function clearAuth() {
    token.value = '';
    user.value = null;
    localStorage.removeItem('token');
  }

  function isAuthenticated() {
    return !!token.value;
  }

  return {
    token,
    user,
    setToken,
    setUser,
    clearAuth,
    isAuthenticated
  };
});

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { gql } from '@apollo/client/core';

import apolloClient from '@/api/apollo';
import http from '@/api/http';

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'student' | 'teacher' | 'admin';
}

const USER_PROFILE_QUERY = gql`
  query UserProfile {
    userProfile {
      id
      username
      email
      firstName
      lastName
      role
    }
  }
`;

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<UserProfile | null>(null);
  const loading = ref(false);
  const profileLoaded = ref(false);

  const isAuthenticated = computed(() => Boolean(currentUser.value));
  const role = computed(() => currentUser.value?.role ?? null);
  const fullName = computed(() => {
    if (!currentUser.value) return '';
    const { firstName, lastName, username } = currentUser.value;
    return `${firstName || ''} ${lastName || ''}`.trim() || username;
  });

  async function fetchProfile() {
    loading.value = true;
    try {
      const { data } = await apolloClient.query({
        query: USER_PROFILE_QUERY,
        fetchPolicy: 'network-only'
      });
      currentUser.value = data?.userProfile ?? null;
    } catch (error) {
      currentUser.value = null;
      throw error;
    } finally {
      loading.value = false;
      profileLoaded.value = true;
    }
  }

  async function login(username: string, password: string) {
    await http.post('/accounts/login/', { username, password });
    await fetchProfile();
  }

  async function register(payload: {
    username: string;
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
    role?: string;
  }) {
    await http.post('/accounts/register/', payload);
    await fetchProfile();
  }

  async function logout() {
    await http.post('/accounts/logout/');
    currentUser.value = null;
  }

  return {
    currentUser,
    loading,
    profileLoaded,
    isAuthenticated,
    role,
    fullName,
    fetchProfile,
    login,
    register,
    logout
  };
});


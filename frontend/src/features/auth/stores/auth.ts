import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { gql } from '@apollo/client/core';

import apolloClient from '@/shared/api/apollo';
import http from '@/shared/api/http';

export interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
}

const USER_PROFILE_QUERY = gql`
  query UserProfile {
    me {
      id
      email
      firstName
      lastName
    }
  }
`;

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<UserProfile | null>(null);
  const loading = ref(false);
  const profileLoaded = ref(false);
  const userRole = ref<string | null>(null);

  const isAuthenticated = computed(() => Boolean(currentUser.value));
  const role = computed(() => userRole.value);
  const fullName = computed(() => {
    if (!currentUser.value) return '';
    const { firstName, lastName, email } = currentUser.value;
    return `${firstName || ''} ${lastName || ''}`.trim() || email;
  });

  async function fetchProfile() {
    loading.value = true;
    try {
      const { data } = await apolloClient.query({
        query: USER_PROFILE_QUERY,
        fetchPolicy: 'network-only'
      });
      currentUser.value = data?.me ?? null;
      
      // Determine role from course memberships
      if (currentUser.value) {
        const membershipQuery = await apolloClient.query({
          query: gql`
            query UserMemberships {
              userCoursesConnection {
                role
              }
            }
          `,
          fetchPolicy: 'network-only'
        });
        const memberships = membershipQuery.data?.userCoursesConnection ?? [];
        if (memberships.some((m: any) => m.role === 'instructor')) {
          userRole.value = 'teacher';
        } else if (memberships.some((m: any) => m.role === 'teaching_assistant')) {
          userRole.value = 'teacher';
        } else {
          userRole.value = 'student';
        }
      }
    } catch (error) {
      currentUser.value = null;
      userRole.value = null;
      throw error;
    } finally {
      loading.value = false;
      profileLoaded.value = true;
    }
  }

  async function login(email: string, password: string) {
    await http.post('/accounts/login/', { email, password });
    await fetchProfile();
  }

  async function register(payload: {
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
  }) {
    await http.post('/accounts/register/', payload);
    await fetchProfile();
  }

  async function logout() {
    await http.post('/accounts/logout/');
    currentUser.value = null;
    userRole.value = null;
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


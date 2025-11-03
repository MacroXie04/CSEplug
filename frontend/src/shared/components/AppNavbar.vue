<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm">
    <div class="container-fluid">
      <button class="btn btn-outline-secondary me-3 d-lg-none" @click="$emit('toggle-sidebar')">
        <i class="bi bi-list"></i>
      </button>
      <span class="navbar-brand fw-semibold">{{ title }}</span>

      <div class="d-flex align-items-center gap-2 ms-auto">
        <button class="btn btn-outline-primary btn-sm" @click="toggleTheme?.()">
          <i class="bi" :class="isDark ? 'bi-sun' : 'bi-moon'" />
        </button>
        <div class="dropdown">
          <button
            class="btn btn-outline-secondary dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i class="bi bi-person-circle me-1"></i>
            {{ auth.fullName }}
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <router-link class="dropdown-item" :to="{ name: 'profile' }">
                <i class="bi bi-person me-2"></i>Profile
              </router-link>
            </li>
            <li><hr class="dropdown-divider" /></li>
            <li>
              <button class="dropdown-item text-danger" @click="handleLogout">
                <i class="bi bi-box-arrow-right me-2"></i>Sign out
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, inject, type Ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/features/auth/stores/auth';

defineProps<{ title: string }>();
defineEmits<{ (e: 'toggle-sidebar'): void }>();

const toggleTheme = inject<() => void>('toggleTheme', undefined);
const darkModeRef = inject<Ref<boolean> | undefined>('isDarkMode', undefined);
const isDark = computed(() => darkModeRef?.value === true);

const auth = useAuthStore();
const router = useRouter();

async function handleLogout() {
  await auth.logout();
  router.push({ name: 'login' });
}
</script>


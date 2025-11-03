<template>
  <div class="layout-wrapper">
    <AppSidebar :items="menuItems" :collapsed="sidebarCollapsed" />
    <div class="layout-content">
      <AppNavbar title="Student Portal" @toggle-sidebar="toggleSidebar" />
      <main class="container-fluid py-4">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import AppNavbar from '@/shared/components/AppNavbar.vue';
import AppSidebar from '@/shared/components/AppSidebar.vue';

const sidebarCollapsed = ref(false);

if (typeof window !== 'undefined' && window.matchMedia('(max-width: 991px)').matches) {
  sidebarCollapsed.value = true;
}

const menuItems = [
  { label: 'Dashboard', icon: 'bi-speedometer2', to: { name: 'student-dashboard' } },
  { label: 'Notes', icon: 'bi-journal-text', to: { name: 'student-notes' } },
  { label: 'Support', icon: 'bi-life-preserver', to: { name: 'student-support' } }
];

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
}
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  min-height: 100vh;
  background-color: #f6f7fb;
}

.layout-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

@media (max-width: 991px) {
  .layout-wrapper {
    position: relative;
  }
}
</style>


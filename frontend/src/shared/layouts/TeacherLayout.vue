<template>
  <div class="layout-wrapper">
    <AppSidebar :items="menuItems" :collapsed="sidebarCollapsed" />
    <div class="layout-content">
      <AppNavbar title="Teacher Portal" @toggle-sidebar="toggleSidebar" />
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
  { label: 'Dashboard', icon: 'bi-graph-up', to: { name: 'teacher-dashboard' } },
  { label: 'Assignments', icon: 'bi-journal-check', to: { name: 'teacher-dashboard', query: { tab: 'assignments' } } },
  { label: 'Notes', icon: 'bi-journal-text', to: { name: 'teacher-notes' } },
  { label: 'Whiteboard', icon: 'bi-easel', to: { name: 'teacher-whiteboard' } },
  { label: 'Support', icon: 'bi-life-preserver', to: { name: 'teacher-support' } }
];

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
}
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  min-height: 100vh;
  background-color: #f4f6fa;
}

.layout-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>


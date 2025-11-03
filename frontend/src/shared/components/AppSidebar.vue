<template>
  <aside :class="['app-sidebar', { 'is-collapsed': collapsed }]">
    <div class="sidebar-header p-3 border-bottom">
      <slot name="header">
        <span class="fw-semibold">CSE Plug</span>
      </slot>
    </div>
    <nav class="nav flex-column p-2">
      <router-link
        v-for="item in items"
        :key="item.to?.name || item.to"
        class="nav-link d-flex align-items-center gap-2"
        :to="item.to"
      >
        <i class="bi" :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

defineProps<{
  items: Array<{ label: string; icon: string; to: RouteLocationRaw }>;
  collapsed?: boolean;
}>();
</script>

<style scoped>
.app-sidebar {
  width: 260px;
  background-color: #ffffff;
  min-height: 100vh;
  border-right: 1px solid rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.app-sidebar.is-collapsed {
  transform: translateX(-100%);
}

@media (max-width: 991px) {
  .app-sidebar {
    position: absolute;
    z-index: 1050;
    top: 56px;
    left: 0;
    height: calc(100vh - 56px);
  }
}

.nav-link {
  color: #4a5568;
  border-radius: 0.5rem;
  padding: 0.65rem 1rem;
}

.nav-link.router-link-active {
  background-color: rgba(27, 110, 243, 0.1);
  color: #1b6ef3;
}
</style>


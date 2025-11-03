<template>
  <span class="badge" :class="badgeClass">
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ role: 'student' | 'teacher' | 'admin' }>();

const badgeClass = computed(() => {
  switch (props.role) {
    case 'teacher':
      return 'bg-primary';
    case 'admin':
      return 'bg-danger';
    default:
      return 'bg-secondary';
  }
});

const label = computed(() => props.role.replace(/^[a-z]/, (s) => s.toUpperCase()));
</script>


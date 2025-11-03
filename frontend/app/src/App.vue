<template>
  <div :class="['app-root', { 'dark-mode': darkMode }]">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted, provide, ref } from 'vue';

const darkMode = ref(false);

onMounted(() => {
  const storedTheme = localStorage.getItem('cseplug-theme');
  if (storedTheme === 'dark') {
    darkMode.value = true;
    document.body.classList.add('dark-mode');
  }
});

function toggleTheme() {
  darkMode.value = !darkMode.value;
  document.body.classList.toggle('dark-mode', darkMode.value);
  localStorage.setItem('cseplug-theme', darkMode.value ? 'dark' : 'light');
}

provide('toggleTheme', toggleTheme);
provide('isDarkMode', darkMode);
</script>

<style scoped>
.app-root {
  min-height: 100vh;
}
</style>


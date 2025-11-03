<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center">
    <div class="card shadow-lg border-0 w-100" style="max-width: 420px;">
      <div class="card-body p-4">
        <h2 class="fw-semibold mb-1 text-center">Welcome to CSE Plug</h2>
        <p class="text-muted text-center mb-4">Sign in with your platform credentials.</p>

        <form @submit.prevent="handleSubmit" class="d-flex flex-column gap-3">
          <div>
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" required autocomplete="email" />
          </div>
          <div>
            <label class="form-label">Password</label>
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-control"
              required
              autocomplete="current-password"
            />
          </div>
          <div class="form-check">
            <input id="showPassword" v-model="showPassword" type="checkbox" class="form-check-input" />
            <label class="form-check-label" for="showPassword">Show password</label>
          </div>

          <button type="submit" class="btn btn-primary w-100" :disabled="submitting">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            Sign in
          </button>

          <p v-if="errorMessage" class="text-danger small mb-0">{{ errorMessage }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const email = ref('');
const password = ref('');
const showPassword = ref(false);
const submitting = ref(false);
const errorMessage = ref('');

const redirectUrl = computed(() => (route.query.redirect as string) || null);

async function handleSubmit() {
  submitting.value = true;
  errorMessage.value = '';
  try {
    await auth.login(email.value, password.value);
    if (auth.role === 'teacher' || auth.role === 'admin') {
      await router.push(redirectUrl.value || { name: 'teacher-dashboard' });
    } else {
      await router.push(redirectUrl.value || { name: 'student-dashboard' });
    }
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || 'Invalid email or password.';
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, rgba(27, 110, 243, 0.2), rgba(27, 110, 243, 0.05));
  padding: 2rem;
}
</style>


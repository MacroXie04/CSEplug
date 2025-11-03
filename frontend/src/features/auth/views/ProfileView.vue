<template>
  <div class="row justify-content-center">
    <div class="col-lg-6">
      <div class="card shadow-sm border-0">
        <div class="card-body p-4">
          <h4 class="fw-semibold mb-3">Profile</h4>
          <p class="text-muted mb-4">Update your personal information for the platform.</p>

          <form @submit.prevent="handleUpdate" class="d-flex flex-column gap-3">
            <div>
              <label class="form-label">Email</label>
              <input type="email" class="form-control" :value="auth.currentUser?.email" disabled />
            </div>

            <div class="row">
              <div class="col-md-6">
                <label class="form-label">First name</label>
                <input v-model="firstName" type="text" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Last name</label>
                <input v-model="lastName" type="text" class="form-control" />
              </div>
            </div>

            <div class="d-flex align-items-center gap-3">
              <RoleBadge v-if="auth.role" :role="auth.role" />
            </div>

            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                Save changes
              </button>
              <p v-if="message" class="mb-0 text-success">{{ message }}</p>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue';
import { gql } from '@apollo/client/core';

import RoleBadge from '@/shared/components/RoleBadge.vue';
import apolloClient from '@/shared/api/apollo';
import { useAuthStore } from '@/features/auth/stores/auth';

const UPDATE_PROFILE_MUTATION = gql`
  mutation UpdateProfile($firstName: String, $lastName: String) {
    updateProfile(firstName: $firstName, lastName: $lastName) {
      user {
        id
        firstName
        lastName
      }
    }
  }
`;

const auth = useAuthStore();

const firstName = ref('');
const lastName = ref('');
const saving = ref(false);
const message = ref('');

watchEffect(() => {
  firstName.value = auth.currentUser?.firstName ?? '';
  lastName.value = auth.currentUser?.lastName ?? '';
});

async function handleUpdate() {
  saving.value = true;
  message.value = '';
  try {
    await apolloClient.mutate({
      mutation: UPDATE_PROFILE_MUTATION,
      variables: { firstName: firstName.value, lastName: lastName.value }
    });
    await auth.fetchProfile();
    message.value = 'Profile updated successfully.';
  } catch (error) {
    message.value = 'Unable to update profile. Please try again.';
  } finally {
    saving.value = false;
  }
}
</script>


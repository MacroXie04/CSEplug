<template>
  <div class="row g-4">
    <div class="col-12">
      <div class="d-flex justify-content-between align-items-center">
        <h3 class="fw-semibold">Teacher Dashboard</h3>
        <RoleBadge v-if="auth.role" :role="auth.role" />
      </div>
      <p class="text-muted">Manage your courses, assignments, and students.</p>
    </div>

    <div class="col-12">
      <section class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="card-title mb-0">Your Courses</h5>
          </div>
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>
          <div v-else class="row g-3">
            <div v-for="membership in memberships" :key="membership.id" class="col-md-4">
              <div class="card h-100 border">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title">{{ membership.course.title }}</h5>
                    <span class="badge bg-primary">{{ membership.role }}</span>
                  </div>
                  <p class="text-muted">{{ membership.course.description || 'No description' }}</p>
                  <div class="d-flex gap-2 mt-3">
                    <router-link
                      class="btn btn-sm btn-outline-primary"
                      :to="{ name: 'teacher-course-assignments', params: { id: membership.course.id } }"
                    >
                      Manage
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
            <p v-if="!memberships.length" class="text-muted">No courses found.</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { gql } from '@apollo/client/core';
import { useQuery } from '@vue/apollo-composable';

import RoleBadge from '@/shared/components/RoleBadge.vue';
import { useAuthStore } from '@/features/auth/stores/auth';

const TEACHER_DASHBOARD_QUERY = gql`
  query TeacherDashboard {
    userCoursesConnection {
      id
      role
      course {
        id
        title
        description
      }
    }
  }
`;

const auth = useAuthStore();
const { result, loading } = useQuery(TEACHER_DASHBOARD_QUERY, undefined, { fetchPolicy: 'network-only' });

const memberships = computed(() =>
  (result.value?.userCoursesConnection ?? []).filter(
    (m: any) => m.role === 'instructor' || m.role === 'teaching_assistant'
  )
);
</script>


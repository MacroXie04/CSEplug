<template>
  <div class="row g-4">
    <div class="col-12">
      <div class="d-flex justify-content-between align-items-center">
        <h3 class="fw-semibold">Dashboard</h3>
        <RoleBadge v-if="auth.currentUser" :role="auth.currentUser.role" />
      </div>
      <p class="text-muted">Here’s what’s happening across your courses.</p>
    </div>

    <div class="col-xl-8">
      <section class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="card-title mb-0">Enrolled Courses</h5>
            <router-link class="btn btn-link" :to="{ name: 'student-dashboard' }">Refresh</router-link>
          </div>
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>
          <div v-else class="row g-3">
            <div v-for="course in courses" :key="course.id" class="col-md-6">
              <CourseCard :course="course">
                <template #badge>
                  <span class="badge bg-light text-dark">{{ course.assignmentsCount }} assignments</span>
                </template>
                <template #actions>
                  <router-link class="btn btn-outline-primary btn-sm" :to="{ name: 'student-course-detail', params: { id: course.id } }">
                    View course
                  </router-link>
                </template>
              </CourseCard>
            </div>
            <p v-if="!courses.length" class="text-muted">You are not enrolled in any courses yet.</p>
          </div>
        </div>
      </section>
    </div>

    <div class="col-xl-4">
      <section class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <h5 class="card-title mb-3">Upcoming assignments</h5>
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border spinner-border-sm" role="status"></div>
          </div>
          <ul v-else class="list-group list-group-flush">
            <li v-for="assignment in assignments" :key="assignment.id" class="list-group-item">
              <div class="d-flex justify-content-between">
                <div>
                  <p class="mb-1 fw-semibold">{{ assignment.title }}</p>
                  <small class="text-muted">Due {{ formatDate(assignment.dueAt) }}</small>
                </div>
                <router-link :to="{ name: 'student-assignment-detail', params: { id: assignment.id } }" class="btn btn-sm btn-outline-primary">
                  Open
                </router-link>
              </div>
            </li>
            <li v-if="!assignments.length" class="list-group-item text-muted">
              No assignments due soon.
            </li>
          </ul>
        </div>
      </section>

      <section class="card border-0 shadow-sm mt-4">
        <div class="card-body">
          <h6 class="fw-semibold mb-2">Latest grades</h6>
          <ul class="list-group list-group-flush">
            <li v-for="grade in grades" :key="grade.id" class="list-group-item px-0 d-flex justify-content-between">
              <span>{{ grade.assignmentTitle }}</span>
              <span class="fw-semibold">{{ grade.score }}</span>
            </li>
            <li v-if="!grades.length" class="list-group-item px-0 text-muted">Grades will appear here after grading.</li>
          </ul>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { gql } from '@apollo/client/core';
import { useQuery } from '@vue/apollo-composable';

import CourseCard from '@/components/CourseCard.vue';
import RoleBadge from '@/components/RoleBadge.vue';
import { useAuthStore } from '@/stores/auth';

const DASHBOARD_QUERY = gql`
  query StudentDashboard {
    courses(activeOnly: true) {
      id
      code
      title
      description
      instructor {
        username
        firstName
      }
      assignments {
        id
      }
    }
    assignments(upcomingOnly: true) {
      id
      title
      dueAt
      instructionsPreview
    }
    grades {
      id
      score
      submission {
        assignment {
          title
        }
      }
    }
  }
`;

const auth = useAuthStore();
const { result, loading } = useQuery(DASHBOARD_QUERY, undefined, { fetchPolicy: 'network-only' });

const courses = computed(() =>
  (result.value?.courses ?? []).map((course: any) => ({
    ...course,
    assignmentsCount: course.assignments?.length ?? 0
  }))
);

const assignments = computed(() => result.value?.assignments ?? []);
const grades = computed(() =>
  (result.value?.grades ?? []).map((grade: any) => ({
    ...grade,
    assignmentTitle: grade.submission?.assignment?.title ?? 'Assignment'
  }))
);

function formatDate(date: string | null | undefined) {
  if (!date) return 'Anytime';
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(date));
}
</script>


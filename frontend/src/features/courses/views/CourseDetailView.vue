<template>
  <div v-if="course" class="course-detail">
    <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
      <div>
        <h2 class="fw-semibold mb-1">{{ course.title }}</h2>
        <p class="text-muted">{{ formatDateRange(course.startDate, course.endDate) }}</p>
      </div>
      <div class="d-flex gap-2">
        <router-link v-if="isTeacher" class="btn btn-primary" :to="{ name: 'teacher-course-assignments', params: { id: course.id } }">
          Manage course
        </router-link>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <section class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <h5 class="card-title fw-semibold">Overview</h5>
            <p class="text-muted">{{ course.description || 'No description yet.' }}</p>
            <div v-if="course.syllabus" class="mt-3">
              <h6 class="fw-semibold">Syllabus</h6>
              <p class="text-muted">{{ course.syllabus }}</p>
            </div>
          </div>
        </section>

        <section class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="card-title">Assignments</h5>
              <router-link
                v-if="isTeacher"
                class="btn btn-sm btn-outline-primary"
                :to="{ name: 'teacher-course-assignments', params: { id: course.id } }"
              >
                New assignment
              </router-link>
            </div>
            <div class="row g-3">
              <div v-for="assignment in assignments" :key="assignment.id" class="col-md-6">
                <AssignmentCard :assignment="assignment">
                  <template #actions>
                    <router-link
                      class="btn btn-outline-primary btn-sm"
                      :to="{ name: 'student-assignment-detail', params: { id: assignment.id } }"
                    >
                      View
                    </router-link>
                  </template>
                </AssignmentCard>
              </div>
            </div>
            <p v-if="!assignments.length" class="text-muted mb-0">Assignments will appear here once published.</p>
          </div>
        </section>
      </div>

      <div class="col-xl-4">
        <section class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <h5 class="card-title">Course Info</h5>
            <div class="mb-3">
              <h6 class="fw-semibold mb-1">Policy</h6>
              <p class="text-muted small">{{ course.policy || 'No policy information.' }}</p>
            </div>
            <div v-if="course.startDate || course.endDate">
              <h6 class="fw-semibold mb-1">Duration</h6>
              <p class="text-muted small">{{ formatDateRange(course.startDate, course.endDate) }}</p>
            </div>
          </div>
        </section>

        <section class="card border-0 shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Notes Pages</h5>
            <ul class="list-group list-group-flush">
              <li v-for="note in notesPages" :key="note.id" class="list-group-item px-0">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <p class="mb-1 fw-semibold">Page {{ note.orderIndex }}</p>
                    <small class="text-muted">{{ formatDate(note.updatedAt) }}</small>
                  </div>
                  <router-link
                    class="btn btn-sm btn-outline-secondary"
                    :to="{ name: 'student-notes', params: { courseId: course.id } }"
                  >
                    View
                  </router-link>
                </div>
              </li>
              <li v-if="!notesPages.length" class="list-group-item px-0 text-muted">Notes will appear here after upload.</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  </div>
  <div v-else-if="loading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status"></div>
  </div>
  <p v-else class="text-danger">Course not found or inaccessible.</p>
</template>

<script setup lang="ts">
/**
 * CourseDetailView Component
 * 
 * Displays detailed information about a course including:
 * - Course metadata (title, description, dates, policy)
 * - List of assignments with links
 * - Notes pages
 * 
 * GraphQL Usage:
 * - Query: course(id) - Fetches course details
 * - Query: assignmentsConnection(courseId) - Fetches course assignments
 * - Query: notesPages(courseId) - Fetches course notes
 * 
 * Example Query:
 * ```graphql
 * query CourseDetail($id: ID!) {
 *   course(id: $id) {
 *     id
 *     title
 *     description
 *   }
 *   assignmentsConnection(courseId: $id) {
 *     id
 *     title
 *     points
 *   }
 * }
 * ```
 * 
 * @see {@link /docs/GRAPHQL_EXAMPLES.md#view-course-details} For usage examples
 */
import { computed, ref } from 'vue';
import { gql } from '@apollo/client/core';
import { useMutation, useQuery } from '@vue/apollo-composable';
import { useRoute } from 'vue-router';

import AssignmentCard from '@/features/assignments/components/AssignmentCard.vue';
import { useAuthStore } from '@/features/auth/stores/auth';

// GraphQL query to fetch course details, assignments, and notes
const COURSE_DETAIL_QUERY = gql`
  query CourseDetail($id: ID!) {
    course(id: $id) {
      id
      title
      description
      syllabus
      policy
      startDate
      endDate
      createdAt
      updatedAt
    }
    assignmentsConnection(courseId: $id) {
      id
      title
      points
      publishAt
      dueAt
      createdAt
      updatedAt
    }
    notesPages(courseId: $id) {
      id
      orderIndex
      thumbnailSrc
      thumbnailDarkSrc
      createdAt
      updatedAt
    }
  }
`;

const route = useRoute();
const auth = useAuthStore();

const courseId = computed(() => route.params.id as string);

const { result, loading } = useQuery(COURSE_DETAIL_QUERY, () => ({ id: courseId.value }), {
  fetchPolicy: 'network-only'
});

const course = computed(() => result.value?.course ?? null);
const assignments = computed(() => result.value?.assignmentsConnection ?? []);
const notesPages = computed(() => result.value?.notesPages ?? []);

const isTeacher = computed(() => auth.role === 'teacher' || auth.role === 'admin');

function formatDate(date: string | null | undefined) {
  if (!date) return '';
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(date));
}

function formatDateRange(startDate: string | null | undefined, endDate: string | null | undefined) {
  if (!startDate && !endDate) return 'No dates set';
  if (!endDate) return `From ${formatDate(startDate)}`;
  if (!startDate) return `Until ${formatDate(endDate)}`;
  return `${formatDate(startDate)} - ${formatDate(endDate)}`;
}
</script>


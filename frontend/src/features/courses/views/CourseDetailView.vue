<template>
  <div v-if="course" class="course-detail">
    <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
      <div>
        <h2 class="fw-semibold mb-1">{{ course.title }}</h2>
        <p class="text-muted mb-1">{{ course.code }}</p>
        <p class="text-muted">Instructor: {{ instructorName }}</p>
      </div>
      <div class="d-flex gap-2">
        <button v-if="canEnroll" class="btn btn-outline-primary" :disabled="enrolling" @click="handleEnroll">
          <span v-if="enrolling" class="spinner-border spinner-border-sm me-2"></span>
          Join course
        </button>
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
              <div v-for="assignment in course.assignments" :key="assignment.id" class="col-md-6">
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
            <p v-if="!course.assignments.length" class="text-muted mb-0">Assignments will appear here once published.</p>
          </div>
        </section>
      </div>

      <div class="col-xl-4">
        <section class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <h5 class="card-title">Announcements</h5>
            <div v-if="!course.announcements.length" class="text-muted">No announcements yet.</div>
            <div v-else class="list-group">
              <div v-for="announcement in course.announcements" :key="announcement.id" class="list-group-item border-0 border-bottom">
                <h6 class="fw-semibold mb-1">{{ announcement.title }}</h6>
                <p class="text-muted small mb-2">{{ formatDate(announcement.createdAt) }}</p>
                <p class="mb-0">{{ announcement.body }}</p>
              </div>
            </div>
          </div>
        </section>

        <section class="card border-0 shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Lecture notes</h5>
            <ul class="list-group list-group-flush">
              <li v-for="note in notes" :key="note.id" class="list-group-item px-0">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <p class="mb-1 fw-semibold">{{ note.title }}</p>
                    <small class="text-muted">{{ note.description || 'No description' }}</small>
                  </div>
                  <a class="btn btn-sm btn-outline-secondary" :href="note.file" target="_blank" rel="noreferrer">
                    Download
                  </a>
                </div>
              </li>
              <li v-if="!notes.length" class="list-group-item px-0 text-muted">Notes will appear here after upload.</li>
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
import { computed, ref } from 'vue';
import { gql } from '@apollo/client/core';
import { useMutation, useQuery } from '@vue/apollo-composable';
import { useRoute } from 'vue-router';

import AssignmentCard from '@/features/assignments/components/AssignmentCard.vue';
import { useAuthStore } from '@/features/auth/stores/auth';

const COURSE_DETAIL_QUERY = gql`
  query CourseDetail($id: ID!) {
    course(id: $id) {
      id
      code
      title
      description
      syllabus
      instructor {
        username
        firstName
        lastName
      }
      announcements {
        id
        title
        body
        createdAt
      }
      assignments {
        id
        title
        dueAt
        isOverdue
        instructionsPreview
      }
    }
    lectureNotes(courseId: $id) {
      id
      title
      description
      file
      publishedAt
    }
  }
`;

const ENROLL_MUTATION = gql`
  mutation Enroll($courseId: ID!) {
    enrollInCourse(courseId: $courseId) {
      course {
        id
      }
    }
  }
`;

const route = useRoute();
const auth = useAuthStore();

const courseId = computed(() => route.params.id as string);
const enrolling = ref(false);

const { result, loading, refetch } = useQuery(COURSE_DETAIL_QUERY, () => ({ id: courseId.value }), {
  fetchPolicy: 'network-only'
});

const notes = computed(() => result.value?.lectureNotes ?? []);
const course = computed(() => result.value?.course ?? null);

const instructorName = computed(() => {
  const instructor = course.value?.instructor;
  if (!instructor) return 'Unknown instructor';
  return `${instructor.firstName || ''} ${instructor.lastName || ''}`.trim() || instructor.username;
});

const isTeacher = computed(() => auth.role === 'teacher' || auth.role === 'admin');
const canEnroll = computed(() => auth.role === 'student');

const { mutate: enrollMutation } = useMutation(ENROLL_MUTATION);

async function handleEnroll() {
  enrolling.value = true;
  try {
    await enrollMutation({ courseId: courseId.value });
    await refetch();
  } finally {
    enrolling.value = false;
  }
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(date));
}
</script>


<template>
  <div v-if="assignment" class="assignment-detail">
    <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
      <div>
        <h2 class="fw-semibold mb-1">{{ assignment.title }}</h2>
        <p class="text-muted mb-1">Course: {{ assignment.course.title }}</p>
        <p class="text-muted">Due {{ formatDate(assignment.dueAt) }} · Max score {{ assignment.maxScore }}</p>
      </div>
      <router-link
        v-if="isTeacher"
        class="btn btn-outline-primary"
        :to="{ name: 'teacher-assignment-submissions', params: { id: assignment.id } }"
      >
        Review submissions
      </router-link>
    </div>

    <div class="row g-4">
      <div class="col-lg-8">
        <section class="card border-0 shadow-sm mb-4">
          <div class="card-body">
            <h5 class="fw-semibold mb-3">Instructions</h5>
            <div v-html="renderMarkdown(assignment.instructionsMarkdown)"></div>
          </div>
        </section>

        <section v-if="isStudent" class="card border-0 shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Your submission</h5>
            <form @submit.prevent="handleSubmit" class="d-flex flex-column gap-3">
              <textarea
                v-model="submissionContent"
                class="form-control"
                rows="10"
                placeholder="Write your markdown answer here..."
                required
              ></textarea>
              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  Submit assignment
                </button>
                <span v-if="submissionMessage" class="text-success">{{ submissionMessage }}</span>
              </div>
            </form>
            <div v-if="currentSubmission" class="mt-4">
              <h6 class="fw-semibold">Last submission</h6>
              <p class="text-muted small">Submitted {{ formatDate(currentSubmission.submittedAt) }}</p>
              <div class="bg-light rounded p-3">
                <pre class="mb-0">{{ currentSubmission.contentMarkdown }}</pre>
              </div>
              <div v-if="currentSubmission.grade" class="alert alert-info mt-3">
                <strong>Score:</strong> {{ currentSubmission.grade.score }}<br />
                <strong>Feedback:</strong>
                <span v-html="renderMarkdown(currentSubmission.grade.feedbackMarkdown)"></span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div class="col-lg-4">
        <section class="card border-0 shadow-sm">
          <div class="card-body">
            <h6 class="fw-semibold">Submission summary</h6>
            <p class="text-muted mb-2">Total submissions: {{ submissions.length }}</p>
            <p class="text-muted mb-2">Last updated: {{ formatDate(assignment.updatedAt) }}</p>
            <div v-if="isTeacher" class="mt-3">
              <h6 class="fw-semibold">Latest submissions</h6>
              <ul class="list-group list-group-flush">
                <li v-for="submission in submissions.slice(0, 5)" :key="submission.id" class="list-group-item px-0 d-flex justify-content-between">
                  <span>{{ submission.student?.username }}</span>
                  <small class="text-muted">{{ timeSince(submission.submittedAt) }} ago</small>
                </li>
                <li v-if="!submissions.length" class="list-group-item px-0 text-muted">No submissions yet.</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
  <div v-else-if="loading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status"></div>
  </div>
  <p v-else class="text-danger">Assignment not found.</p>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { gql } from '@apollo/client/core';
import { useMutation, useQuery } from '@vue/apollo-composable';
import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import { useRoute } from 'vue-router';

import { useAuthStore } from '@/features/auth/stores/auth';

const ASSIGNMENT_DETAIL_QUERY = gql`
  query AssignmentDetail($id: ID!) {
    assignment(id: $id) {
      id
      title
      instructionsMarkdown
      dueAt
      maxScore
      updatedAt
      course {
        id
        title
      }
    }
    submissions(assignmentId: $id) {
      id
      contentMarkdown
      submittedAt
      student {
        username
      }
      grade {
        id
        score
        feedbackMarkdown
        gradedAt
        grader {
          username
        }
      }
    }
  }
`;

const SUBMIT_MUTATION = gql`
  mutation SubmitAssignment($id: ID!, $content: String!) {
    submitAssignment(assignmentId: $id, contentMarkdown: $content) {
      submission {
        id
        submittedAt
        contentMarkdown
        grade {
          score
          feedbackMarkdown
        }
      }
    }
  }
`;

const md = new MarkdownIt({ linkify: true, breaks: true });

const route = useRoute();
const auth = useAuthStore();
const assignmentId = computed(() => route.params.id as string);

const { result, loading, refetch } = useQuery(ASSIGNMENT_DETAIL_QUERY, () => ({ id: assignmentId.value }), {
  fetchPolicy: 'network-only'
});

const submissions = computed(() => result.value?.submissions ?? []);
const assignment = computed(() => result.value?.assignment ?? null);
const isTeacher = computed(() => auth.role === 'teacher' || auth.role === 'admin');
const isStudent = computed(() => auth.role === 'student');

const currentSubmission = computed(() => {
  if (!isStudent.value) return null;
  if (!auth.currentUser) return null;
  return submissions.value.find((submission: any) => submission.student?.username === auth.currentUser?.username) ?? null;
});

const submissionContent = ref('');
const submitting = ref(false);
const submissionMessage = ref('');

watch(currentSubmission, (value) => {
  if (value) {
    submissionContent.value = value.contentMarkdown;
  }
});

const { mutate: submitMutation } = useMutation(SUBMIT_MUTATION);

async function handleSubmit() {
  submitting.value = true;
  submissionMessage.value = '';
  try {
    await submitMutation({ id: assignmentId.value, content: submissionContent.value });
    await refetch();
    submissionMessage.value = 'Submission saved successfully.';
  } finally {
    submitting.value = false;
  }
}

function renderMarkdown(content: string) {
  return DOMPurify.sanitize(md.render(content || ''));
}

function formatDate(date: string | null | undefined) {
  if (!date) return 'No deadline';
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(date));
}

function timeSince(date: string) {
  const diff = Date.now() - new Date(date).getTime();
  const hours = Math.max(Math.floor(diff / (1000 * 60 * 60)), 0);
  if (hours < 1) {
    const minutes = Math.max(Math.floor(diff / (1000 * 60)), 0);
    return `${minutes}m`;
  }
  if (hours < 24) {
    return `${hours}h`;
  }
  const days = Math.floor(hours / 24);
  return `${days}d`;
}
</script>


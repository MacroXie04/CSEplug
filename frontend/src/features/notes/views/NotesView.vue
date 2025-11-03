<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
        <div>
          <h4 class="fw-semibold mb-0">Lecture notes</h4>
          <p class="text-muted mb-0">Download lecture materials for your enrolled courses.</p>
        </div>
        <div class="input-group" style="max-width: 260px;">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input v-model="search" type="search" class="form-control" placeholder="Search notes" />
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else class="table-responsive">
        <table class="table align-middle">
          <thead>
            <tr>
              <th>Title</th>
              <th>Course</th>
              <th>Published</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="note in filteredNotes" :key="note.id">
              <td>
                <div class="fw-semibold">{{ note.title }}</div>
                <div class="text-muted small">{{ note.description || 'No description' }}</div>
              </td>
              <td>{{ note.course.title }}</td>
              <td>{{ formatDate(note.publishedAt) }}</td>
              <td class="text-end">
                <a class="btn btn-sm btn-outline-primary" :href="note.file" target="_blank" rel="noreferrer">
                  <i class="bi bi-download me-2"></i>Download
                </a>
              </td>
            </tr>
            <tr v-if="!filteredNotes.length">
              <td colspan="4" class="text-center text-muted py-4">No notes found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { gql } from '@apollo/client/core';
import { useQuery } from '@vue/apollo-composable';

const NOTES_QUERY = gql`
  query LectureNotes {
    lectureNotes {
      id
      title
      description
      file
      publishedAt
      course {
        id
        title
      }
    }
  }
`;

const search = ref('');
const { result, loading } = useQuery(NOTES_QUERY, undefined, { fetchPolicy: 'network-only' });

const notes = computed(() => result.value?.lectureNotes ?? []);

const filteredNotes = computed(() => {
  const query = search.value.trim().toLowerCase();
  if (!query) return notes.value;
  return notes.value.filter((note: any) =>
    [note.title, note.description, note.course?.title]
      .filter(Boolean)
      .some((field: string) => field.toLowerCase().includes(query))
  );
});

function formatDate(date: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(date));
}
</script>


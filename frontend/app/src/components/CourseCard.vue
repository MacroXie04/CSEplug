<template>
  <div class="card h-100 shadow-sm">
    <div class="card-body d-flex flex-column">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <h5 class="card-title mb-1">{{ course.title }}</h5>
          <p class="text-muted small mb-0">{{ course.code }}</p>
        </div>
        <slot name="badge"></slot>
      </div>
      <p class="card-text text-muted flex-grow-1">
        {{ course.description || 'No description provided yet.' }}
      </p>
      <div class="d-flex justify-content-between align-items-center mt-3">
        <span class="text-muted small">Instructor: {{ course.instructor?.firstName || course.instructor?.username }}</span>
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface CourseSummary {
  id: string;
  code: string;
  title: string;
  description?: string | null;
  instructor?: {
    username: string;
    firstName?: string | null;
  } | null;
}

defineProps<{ course: CourseSummary }>();
</script>


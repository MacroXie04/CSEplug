<template>
  <div class="card h-100 border-0 shadow-sm">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h5 class="card-title mb-1">{{ assignment.title }}</h5>
          <p class="text-muted small mb-0">Due {{ dueLabel }}</p>
        </div>
        <span class="badge" :class="assignment.isOverdue ? 'bg-danger' : 'bg-success'">
          {{ assignment.isOverdue ? 'Overdue' : 'Open' }}
        </span>
      </div>
      <p class="card-text text-muted mt-3">
        {{ assignment.instructionsPreview }}
      </p>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export interface AssignmentSummary {
  id: string;
  title: string;
  dueAt?: string | null;
  isOverdue: boolean;
  instructionsPreview: string;
}

const props = defineProps<{ assignment: AssignmentSummary }>();

const dueLabel = computed(() => {
  if (!props.assignment.dueAt) return 'Anytime';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(props.assignment.dueAt));
});
</script>


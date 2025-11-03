# GraphQL Frontend Integration Examples

This document provides practical examples of integrating the CSEplug GraphQL API with the Vue.js frontend.

## Table of Contents

- [Setup](#setup)
- [Basic Patterns](#basic-patterns)
  - [Simple Query](#simple-query)
  - [Query with Variables](#query-with-variables)
  - [Simple Mutation](#simple-mutation)
  - [Mutation with Error Handling](#mutation-with-error-handling)
- [Authentication](#authentication)
  - [Login Flow](#login-flow)
  - [Logout Flow](#logout-flow)
  - [Protected Route](#protected-route)
- [Course Management](#course-management)
  - [List User Courses](#list-user-courses)
  - [View Course Details](#view-course-details)
  - [Create a Course](#create-a-course)
  - [Add Students to Course](#add-students-to-course)
- [Assignments](#assignments)
  - [List Assignments](#list-assignments)
  - [Create Assignment](#create-assignment)
  - [Submit Assignment](#submit-assignment)
  - [Grade Submission](#grade-submission)
- [Support System](#support-system)
  - [Create Support Ticket](#create-support-ticket)
  - [List Tickets](#list-tickets)
  - [Send Chat Message](#send-chat-message)
- [Whiteboard](#whiteboard)
  - [Create Whiteboard Session](#create-whiteboard-session)
  - [Add Strokes](#add-strokes)
- [Advanced Patterns](#advanced-patterns)
  - [Optimistic Updates](#optimistic-updates)
  - [Pagination](#pagination)
  - [Real-time Updates with Polling](#real-time-updates-with-polling)
  - [Error Recovery](#error-recovery)

---

## Setup

Before using GraphQL in your components, ensure Apollo Client is properly configured in your app:

```typescript
// main.ts
import { createApp } from 'vue';
import { DefaultApolloClient } from '@vue/apollo-composable';
import apolloClient from '@/shared/api/apollo';
import App from './App.vue';

const app = createApp(App);
app.provide(DefaultApolloClient, apolloClient);
app.mount('#app');
```

---

## Basic Patterns

### Simple Query

Fetch data when component mounts:

```vue
<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">Error: {{ error.message }}</div>
  <div v-else>
    <h1>Hello, {{ result?.me?.firstName }}!</h1>
  </div>
</template>

<script setup lang="ts">
import { useQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const { result, loading, error } = useQuery(gql`
  query GetCurrentUser {
    me {
      id
      email
      firstName
      lastName
    }
  }
`);
</script>
```

---

### Query with Variables

Pass dynamic parameters to queries:

```vue
<template>
  <div v-if="loading">Loading course...</div>
  <div v-else-if="course">
    <h1>{{ course.title }}</h1>
    <p>{{ course.description }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const route = useRoute();
const courseId = computed(() => route.params.id as string);

const COURSE_QUERY = gql`
  query GetCourse($id: ID!) {
    course(id: $id) {
      id
      title
      description
      syllabus
      startDate
      endDate
    }
  }
`;

const { result, loading } = useQuery(
  COURSE_QUERY,
  () => ({ id: courseId.value }), // Variables as a function for reactivity
  {
    fetchPolicy: 'cache-first' // or 'network-only', 'cache-and-network'
  }
);

const course = computed(() => result.value?.course);
</script>
```

---

### Simple Mutation

Perform a mutation operation:

```vue
<template>
  <button @click="handleUpdate" :disabled="loading">
    {{ loading ? 'Updating...' : 'Update Profile' }}
  </button>
</template>

<script setup lang="ts">
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const UPDATE_PROFILE = gql`
  mutation UpdateProfile($firstName: String!, $lastName: String!) {
    updateProfile(firstName: $firstName, lastName: $lastName) {
      user {
        id
        firstName
        lastName
      }
    }
  }
`;

const { mutate, loading } = useMutation(UPDATE_PROFILE);

async function handleUpdate() {
  const result = await mutate({
    firstName: 'Jane',
    lastName: 'Doe'
  });
  
  console.log('Updated user:', result?.data.updateProfile.user);
}
</script>
```

---

### Mutation with Error Handling

Handle errors gracefully:

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="title" placeholder="Course title" required />
    <button type="submit" :disabled="loading">Create Course</button>
    <div v-if="error" class="error">{{ error.message }}</div>
    <div v-if="success" class="success">Course created successfully!</div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const title = ref('');
const error = ref<Error | null>(null);
const success = ref(false);

const CREATE_COURSE = gql`
  mutation CreateCourse($title: String!) {
    courseCreate(title: $title) {
      course {
        id
        title
      }
    }
  }
`;

const { mutate, loading } = useMutation(CREATE_COURSE);

async function handleSubmit() {
  error.value = null;
  success.value = false;
  
  try {
    await mutate({ title: title.value });
    success.value = true;
    title.value = ''; // Reset form
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

## Authentication

### Login Flow

Complete login implementation with error handling:

```vue
<template>
  <form @submit.prevent="handleLogin">
    <div>
      <label>Email</label>
      <input v-model="email" type="email" required />
    </div>
    <div>
      <label>Password</label>
      <input v-model="password" type="password" required />
    </div>
    <button type="submit" :disabled="loading">
      {{ loading ? 'Logging in...' : 'Login' }}
    </button>
    <div v-if="error" class="error">{{ error.message }}</div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';
import { useAuthStore } from '@/features/auth/stores/auth';

const router = useRouter();
const auth = useAuthStore();

const email = ref('');
const password = ref('');
const error = ref<Error | null>(null);

const LOGIN_MUTATION = gql`
  mutation Login($email: String!, $password: String!) {
    login(email: $email, password: $password) {
      user {
        id
        email
        firstName
        lastName
      }
      success
    }
  }
`;

const { mutate, loading } = useMutation(LOGIN_MUTATION);

async function handleLogin() {
  error.value = null;
  
  try {
    const result = await mutate({
      email: email.value,
      password: password.value
    });
    
    if (result?.data.login.success) {
      // Update auth store
      await auth.fetchProfile();
      
      // Redirect to dashboard
      router.push({ name: 'dashboard' });
    }
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

### Logout Flow

```vue
<template>
  <button @click="handleLogout" :disabled="loading">
    Logout
  </button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';
import apolloClient from '@/shared/api/apollo';
import { useAuthStore } from '@/features/auth/stores/auth';

const router = useRouter();
const auth = useAuthStore();

const LOGOUT_MUTATION = gql`
  mutation Logout {
    logout {
      success
    }
  }
`;

const { mutate, loading } = useMutation(LOGOUT_MUTATION);

async function handleLogout() {
  try {
    await mutate();
    
    // Clear Apollo cache
    await apolloClient.clearStore();
    
    // Clear auth store
    auth.currentUser = null;
    auth.userRole = null;
    
    // Redirect to login
    router.push({ name: 'login' });
  } catch (e) {
    console.error('Logout failed:', e);
  }
}
</script>
```

---

### Protected Route

Check authentication before allowing access:

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/features/auth/stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/features/dashboard/views/StudentDashboardView.vue'),
      meta: { requiresAuth: true }
    },
    // ... other routes
  ]
});

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  
  // Load user profile if not loaded
  if (!auth.profileLoaded) {
    try {
      await auth.fetchProfile();
    } catch (e) {
      // User not authenticated
    }
  }
  
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
  } else {
    next();
  }
});

export default router;
```

---

## Course Management

### List User Courses

Display all courses a user is enrolled in:

```vue
<template>
  <div>
    <h2>My Courses</h2>
    <div v-if="loading">Loading courses...</div>
    <div v-else class="course-grid">
      <div v-for="membership in courses" :key="membership.id" class="course-card">
        <h3>{{ membership.course.title }}</h3>
        <p>{{ membership.course.description }}</p>
        <span class="badge">{{ membership.role }}</span>
        <router-link :to="{ name: 'course-detail', params: { id: membership.course.id } }">
          View Course
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const COURSES_QUERY = gql`
  query GetMyCourses {
    userCoursesConnection {
      id
      role
      joinedAt
      course {
        id
        title
        description
        startDate
        endDate
      }
    }
  }
`;

const { result, loading } = useQuery(COURSES_QUERY, null, {
  fetchPolicy: 'cache-and-network'
});

const courses = computed(() => result.value?.userCoursesConnection ?? []);
</script>
```

---

### View Course Details

Fetch comprehensive course information:

```vue
<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="course">
    <header>
      <h1>{{ course.title }}</h1>
      <p>{{ formatDateRange(course.startDate, course.endDate) }}</p>
    </header>
    
    <section>
      <h2>Description</h2>
      <p>{{ course.description }}</p>
    </section>
    
    <section>
      <h2>Assignments ({{ assignments.length }})</h2>
      <div v-for="assignment in assignments" :key="assignment.id">
        <h3>{{ assignment.title }}</h3>
        <p>Due: {{ formatDate(assignment.dueAt) }}</p>
        <p>Points: {{ assignment.points }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const route = useRoute();
const courseId = computed(() => route.params.id as string);

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
    }
    assignmentsConnection(courseId: $id) {
      id
      title
      points
      publishAt
      dueAt
    }
  }
`;

const { result, loading } = useQuery(COURSE_DETAIL_QUERY, () => ({ id: courseId.value }));

const course = computed(() => result.value?.course);
const assignments = computed(() => result.value?.assignmentsConnection ?? []);

function formatDate(date: string | null) {
  if (!date) return 'No deadline';
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(date));
}

function formatDateRange(start: string | null, end: string | null) {
  if (!start && !end) return 'No dates set';
  if (!end) return `From ${formatDate(start)}`;
  if (!start) return `Until ${formatDate(end)}`;
  return `${formatDate(start)} - ${formatDate(end)}`;
}
</script>
```

---

### Create a Course

Create a new course with form validation:

```vue
<template>
  <form @submit.prevent="handleSubmit" class="course-form">
    <h2>Create New Course</h2>
    
    <div class="form-group">
      <label>Title *</label>
      <input v-model="form.title" required />
    </div>
    
    <div class="form-group">
      <label>Description</label>
      <textarea v-model="form.description" rows="4"></textarea>
    </div>
    
    <div class="form-group">
      <label>Syllabus</label>
      <textarea v-model="form.syllabus" rows="6"></textarea>
    </div>
    
    <div class="form-group">
      <label>Policy</label>
      <textarea v-model="form.policy" rows="4"></textarea>
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label>Start Date</label>
        <input v-model="form.startDate" type="date" />
      </div>
      
      <div class="form-group">
        <label>End Date</label>
        <input v-model="form.endDate" type="date" />
      </div>
    </div>
    
    <button type="submit" :disabled="loading">
      {{ loading ? 'Creating...' : 'Create Course' }}
    </button>
    
    <div v-if="error" class="error">{{ error.message }}</div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const router = useRouter();
const error = ref<Error | null>(null);

const form = reactive({
  title: '',
  description: '',
  syllabus: '',
  policy: '',
  startDate: '',
  endDate: ''
});

const CREATE_COURSE_MUTATION = gql`
  mutation CreateCourse(
    $title: String!
    $description: String
    $syllabus: String
    $policy: String
    $startDate: Date
    $endDate: Date
  ) {
    courseCreate(
      title: $title
      description: $description
      syllabus: $syllabus
      policy: $policy
      startDate: $startDate
      endDate: $endDate
    ) {
      course {
        id
        title
        description
      }
    }
  }
`;

const { mutate, loading } = useMutation(CREATE_COURSE_MUTATION);

async function handleSubmit() {
  error.value = null;
  
  try {
    const result = await mutate({
      title: form.title,
      description: form.description || null,
      syllabus: form.syllabus || null,
      policy: form.policy || null,
      startDate: form.startDate || null,
      endDate: form.endDate || null
    });
    
    const courseId = result?.data.courseCreate.course.id;
    router.push({ name: 'course-detail', params: { id: courseId } });
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

### Add Students to Course

Add users to a course by email:

```vue
<template>
  <div class="add-student">
    <h3>Add Student</h3>
    <form @submit.prevent="handleAddStudent">
      <input 
        v-model="email" 
        type="email" 
        placeholder="student@example.com" 
        required 
      />
      <select v-model="role" required>
        <option value="student">Student</option>
        <option value="teaching_assistant">Teaching Assistant</option>
        <option value="instructor">Instructor</option>
      </select>
      <button type="submit" :disabled="loading">Add</button>
    </form>
    <div v-if="error" class="error">{{ error.message }}</div>
    <div v-if="success" class="success">User added successfully!</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  courseId: string;
}

const props = defineProps<Props>();
const emit = defineEmits(['added']);

const email = ref('');
const role = ref('student');
const error = ref<Error | null>(null);
const success = ref(false);

const ADD_MEMBER_MUTATION = gql`
  mutation AddCourseMember($courseId: ID!, $userEmail: String!, $role: String!) {
    courseMembershipAdd(courseId: $courseId, userEmail: $userEmail, role: $role) {
      membership {
        id
        role
        user {
          id
          email
          firstName
          lastName
        }
      }
    }
  }
`;

const { mutate, loading } = useMutation(ADD_MEMBER_MUTATION);

async function handleAddStudent() {
  error.value = null;
  success.value = false;
  
  try {
    const result = await mutate({
      courseId: props.courseId,
      userEmail: email.value,
      role: role.value
    });
    
    success.value = true;
    email.value = '';
    emit('added', result?.data.courseMembershipAdd.membership);
    
    setTimeout(() => {
      success.value = false;
    }, 3000);
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

## Assignments

### List Assignments

Display assignments for a course:

```vue
<template>
  <div class="assignments">
    <h2>Assignments</h2>
    <div v-if="loading">Loading assignments...</div>
    <div v-else>
      <div v-for="assignment in assignments" :key="assignment.id" class="assignment-card">
        <h3>{{ assignment.title }}</h3>
        <div class="metadata">
          <span>Points: {{ assignment.points }}</span>
          <span :class="{ overdue: isOverdue(assignment.dueAt) }">
            Due: {{ formatDate(assignment.dueAt) }}
          </span>
        </div>
        <router-link :to="{ name: 'assignment-detail', params: { id: assignment.id } }">
          View Assignment
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  courseId: string;
}

const props = defineProps<Props>();

const ASSIGNMENTS_QUERY = gql`
  query GetAssignments($courseId: ID!) {
    assignmentsConnection(courseId: $courseId) {
      id
      title
      points
      publishAt
      dueAt
      createdAt
    }
  }
`;

const { result, loading } = useQuery(ASSIGNMENTS_QUERY, { courseId: props.courseId });

const assignments = computed(() => result.value?.assignmentsConnection ?? []);

function formatDate(date: string | null) {
  if (!date) return 'No deadline';
  return new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(new Date(date));
}

function isOverdue(dueAt: string | null) {
  if (!dueAt) return false;
  return new Date(dueAt) < new Date();
}
</script>
```

---

### Create Assignment

Create a new assignment with questions:

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <h2>Create Assignment</h2>
    
    <div class="form-group">
      <label>Title *</label>
      <input v-model="form.title" required />
    </div>
    
    <div class="form-group">
      <label>Instructions (Markdown)</label>
      <textarea v-model="form.instructionsMd" rows="10"></textarea>
    </div>
    
    <div class="form-group">
      <label>Total Points</label>
      <input v-model.number="form.points" type="number" min="0" />
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label>Publish At</label>
        <input v-model="form.publishAt" type="datetime-local" />
      </div>
      
      <div class="form-group">
        <label>Due At</label>
        <input v-model="form.dueAt" type="datetime-local" />
      </div>
    </div>
    
    <button type="submit" :disabled="loading">
      {{ loading ? 'Creating...' : 'Create Assignment' }}
    </button>
    
    <div v-if="error" class="error">{{ error.message }}</div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  courseId: string;
}

const props = defineProps<Props>();
const router = useRouter();
const error = ref<Error | null>(null);

const form = reactive({
  title: '',
  instructionsMd: '',
  points: 100,
  publishAt: '',
  dueAt: ''
});

const CREATE_ASSIGNMENT_MUTATION = gql`
  mutation CreateAssignment(
    $courseId: ID!
    $title: String!
    $instructionsMd: String
    $points: Float
    $publishAt: DateTime
    $dueAt: DateTime
  ) {
    assignmentCreate(
      courseId: $courseId
      title: $title
      instructionsMd: $instructionsMd
      points: $points
      publishAt: $publishAt
      dueAt: $dueAt
    ) {
      assignment {
        id
        title
        points
        dueAt
      }
    }
  }
`;

const { mutate, loading } = useMutation(CREATE_ASSIGNMENT_MUTATION);

async function handleSubmit() {
  error.value = null;
  
  try {
    const result = await mutate({
      courseId: props.courseId,
      title: form.title,
      instructionsMd: form.instructionsMd || null,
      points: form.points,
      publishAt: form.publishAt ? new Date(form.publishAt).toISOString() : null,
      dueAt: form.dueAt ? new Date(form.dueAt).toISOString() : null
    });
    
    const assignmentId = result?.data.assignmentCreate.assignment.id;
    router.push({ name: 'assignment-detail', params: { id: assignmentId } });
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

### Submit Assignment

Submit a response to an assignment question:

```vue
<template>
  <div class="submission">
    <h3>{{ question.title || 'Question' }}</h3>
    <p>{{ question.questionText }}</p>
    
    <form @submit.prevent="handleSubmit">
      <textarea 
        v-if="question.type === 'free_response'"
        v-model="answer"
        rows="10"
        placeholder="Your answer..."
        required
      ></textarea>
      
      <div v-else-if="question.type === 'multiple_choice'" class="options">
        <label v-for="option in question.options" :key="option.id">
          <input 
            type="radio" 
            :value="option.id" 
            v-model="selectedOption"
            required
          />
          {{ option.optionText }}
        </label>
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? 'Submitting...' : 'Submit Answer' }}
      </button>
      
      <div v-if="submitted" class="success">Submitted successfully!</div>
      <div v-if="error" class="error">{{ error.message }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  questionId: string;
  question: {
    type: string;
    title?: string;
    questionText: string;
    options?: Array<{ id: string; optionText: string }>;
  };
}

const props = defineProps<Props>();

const answer = ref('');
const selectedOption = ref('');
const submitted = ref(false);
const error = ref<Error | null>(null);

const SUBMIT_MUTATION = gql`
  mutation SubmitAnswer(
    $assignmentQuestionId: ID!
    $freeResponseText: String
    $multipleChoiceOptionId: ID
  ) {
    assignmentSubmissionCreate(
      assignmentQuestionId: $assignmentQuestionId
      freeResponseText: $freeResponseText
      multipleChoiceOptionId: $multipleChoiceOptionId
    ) {
      submission {
        id
        freeResponseText
        multipleChoiceOption {
          id
          optionText
        }
        createdAt
      }
    }
  }
`;

const { mutate, loading } = useMutation(SUBMIT_MUTATION);

async function handleSubmit() {
  error.value = null;
  submitted.value = false;
  
  try {
    await mutate({
      assignmentQuestionId: props.questionId,
      freeResponseText: props.question.type === 'free_response' ? answer.value : null,
      multipleChoiceOptionId: props.question.type === 'multiple_choice' ? selectedOption.value : null
    });
    
    submitted.value = true;
    
    setTimeout(() => {
      submitted.value = false;
    }, 3000);
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

### Grade Submission

Grade a student's submission (instructor/TA):

```vue
<template>
  <div class="grading">
    <h3>Grade Submission</h3>
    
    <div class="submission-content">
      <p><strong>Student:</strong> {{ submission.user.email }}</p>
      <p><strong>Submitted:</strong> {{ formatDate(submission.createdAt) }}</p>
      <p><strong>Answer:</strong></p>
      <div class="answer">{{ submission.freeResponseText || submission.multipleChoiceOption?.optionText }}</div>
    </div>
    
    <form @submit.prevent="handleGrade">
      <div class="form-group">
        <label>Score *</label>
        <input v-model.number="score" type="number" min="0" step="0.1" required />
      </div>
      
      <div class="form-group">
        <label>Feedback (Markdown)</label>
        <textarea v-model="feedback" rows="6"></textarea>
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? 'Saving...' : 'Save Grade' }}
      </button>
      
      <div v-if="saved" class="success">Grade saved!</div>
      <div v-if="error" class="error">{{ error.message }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  submission: {
    id: string;
    user: { email: string };
    freeResponseText?: string;
    multipleChoiceOption?: { optionText: string };
    createdAt: string;
  };
}

const props = defineProps<Props>();

const score = ref(0);
const feedback = ref('');
const saved = ref(false);
const error = ref<Error | null>(null);

const GRADE_MUTATION = gql`
  mutation GradeSubmission($submissionId: ID!, $score: Float!, $feedbackMd: String) {
    assignmentSubmissionOutcomeUpdate(
      submissionId: $submissionId
      score: $score
      feedbackMd: $feedbackMd
    ) {
      outcome {
        id
        score
        feedbackMd
        isEvaluated
        updatedAt
      }
    }
  }
`;

const { mutate, loading } = useMutation(GRADE_MUTATION);

async function handleGrade() {
  error.value = null;
  saved.value = false;
  
  try {
    await mutate({
      submissionId: props.submission.id,
      score: score.value,
      feedbackMd: feedback.value || null
    });
    
    saved.value = true;
    
    setTimeout(() => {
      saved.value = false;
    }, 3000);
  } catch (e) {
    error.value = e as Error;
  }
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(date));
}
</script>
```

---

## Support System

### Create Support Ticket

```vue
<template>
  <form @submit.prevent="handleSubmit" class="ticket-form">
    <h2>Create Support Ticket</h2>
    
    <div class="form-group">
      <label>Related Course (optional)</label>
      <select v-model="courseId">
        <option value="">General Question</option>
        <option v-for="course in courses" :key="course.id" :value="course.id">
          {{ course.title }}
        </option>
      </select>
    </div>
    
    <div class="form-group">
      <label>Subject *</label>
      <input v-model="subject" required />
    </div>
    
    <div class="form-group">
      <label>Description *</label>
      <textarea v-model="description" rows="6" required></textarea>
    </div>
    
    <button type="submit" :disabled="loading">
      {{ loading ? 'Creating...' : 'Create Ticket' }}
    </button>
    
    <div v-if="error" class="error">{{ error.message }}</div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useQuery, useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const router = useRouter();

const courseId = ref('');
const subject = ref('');
const description = ref('');
const error = ref<Error | null>(null);

// Get user's courses
const COURSES_QUERY = gql`
  query GetCourses {
    userCoursesConnection {
      course {
        id
        title
      }
    }
  }
`;

const { result } = useQuery(COURSES_QUERY);
const courses = computed(() => result.value?.userCoursesConnection.map((m: any) => m.course) ?? []);

// Create ticket mutation
const CREATE_TICKET_MUTATION = gql`
  mutation CreateTicket($courseId: ID, $subject: String!, $description: String!) {
    supportTicketCreate(courseId: $courseId, subject: $subject, description: $description) {
      ticket {
        id
        subject
        status
        createdAt
      }
    }
  }
`;

const { mutate, loading } = useMutation(CREATE_TICKET_MUTATION);

async function handleSubmit() {
  error.value = null;
  
  try {
    const result = await mutate({
      courseId: courseId.value || null,
      subject: subject.value,
      description: description.value
    });
    
    const ticketId = result?.data.supportTicketCreate.ticket.id;
    router.push({ name: 'support-ticket', params: { id: ticketId } });
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

### List Tickets

```vue
<template>
  <div class="tickets">
    <h2>Support Tickets</h2>
    <div v-if="loading">Loading tickets...</div>
    <div v-else>
      <div v-for="ticket in tickets" :key="ticket.id" class="ticket-card">
        <div class="ticket-header">
          <h3>{{ ticket.subject }}</h3>
          <span :class="`badge badge-${ticket.status}`">
            {{ ticket.status }}
          </span>
        </div>
        <p>{{ ticket.description }}</p>
        <div class="ticket-meta">
          <span>Created: {{ formatDate(ticket.createdAt) }}</span>
          <span v-if="ticket.course">Course: {{ ticket.course.title }}</span>
        </div>
        <router-link :to="{ name: 'support-ticket', params: { id: ticket.id } }">
          View Ticket
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const TICKETS_QUERY = gql`
  query GetTickets {
    supportTickets {
      id
      subject
      description
      status
      createdAt
      course {
        id
        title
      }
    }
  }
`;

const { result, loading } = useQuery(TICKETS_QUERY, null, {
  pollInterval: 30000 // Poll every 30 seconds for updates
});

const tickets = computed(() => result.value?.supportTickets ?? []);

function formatDate(date: string) {
  return new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(new Date(date));
}
</script>
```

---

### Send Chat Message

```vue
<template>
  <div class="chat">
    <div class="messages" ref="messagesContainer">
      <div v-for="message in messages" :key="message.id" class="message">
        <div class="message-header">
          <strong>{{ message.author.email }}</strong>
          <span class="time">{{ formatTime(message.createdAt) }}</span>
        </div>
        <p>{{ message.content }}</p>
      </div>
    </div>
    
    <form @submit.prevent="handleSend" class="message-form">
      <input 
        v-model="newMessage" 
        placeholder="Type a message..." 
        :disabled="loading"
        required
      />
      <button type="submit" :disabled="loading">Send</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue';
import { useQuery, useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  ticketId: string;
}

const props = defineProps<Props>();

const newMessage = ref('');
const messagesContainer = ref<HTMLElement>();

// Get messages
const MESSAGES_QUERY = gql`
  query GetTicketMessages($id: ID!) {
    supportTicket(id: $id) {
      id
      messages {
        id
        content
        author {
          id
          email
          firstName
          lastName
        }
        createdAt
      }
    }
  }
`;

const { result, refetch } = useQuery(MESSAGES_QUERY, { id: props.ticketId }, {
  pollInterval: 5000 // Poll every 5 seconds for new messages
});

const messages = computed(() => result.value?.supportTicket.messages ?? []);

// Send message
const SEND_MESSAGE_MUTATION = gql`
  mutation SendMessage($ticketId: ID!, $content: String!) {
    chatMessageCreate(ticketId: $ticketId, content: $content) {
      message {
        id
        content
        createdAt
      }
    }
  }
`;

const { mutate, loading } = useMutation(SEND_MESSAGE_MUTATION);

async function handleSend() {
  if (!newMessage.value.trim()) return;
  
  try {
    await mutate({
      ticketId: props.ticketId,
      content: newMessage.value
    });
    
    newMessage.value = '';
    await refetch(); // Refresh messages
    scrollToBottom();
  } catch (e) {
    console.error('Failed to send message:', e);
  }
}

function formatTime(date: string) {
  return new Intl.DateTimeFormat('en-US', { timeStyle: 'short' }).format(new Date(date));
}

async function scrollToBottom() {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

// Scroll to bottom when messages change
watch(messages, scrollToBottom);
</script>
```

---

## Whiteboard

### Create Whiteboard Session

```vue
<template>
  <form @submit.prevent="handleCreate">
    <h2>Create Whiteboard Session</h2>
    
    <div class="form-group">
      <label>Session Title *</label>
      <input v-model="title" required />
    </div>
    
    <button type="submit" :disabled="loading">
      {{ loading ? 'Creating...' : 'Create Session' }}
    </button>
    
    <div v-if="error" class="error">{{ error.message }}</div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  courseId: string;
}

const props = defineProps<Props>();
const router = useRouter();

const title = ref('');
const error = ref<Error | null>(null);

const CREATE_SESSION_MUTATION = gql`
  mutation CreateWhiteboardSession($courseId: ID!, $title: String!) {
    whiteboardSessionCreate(courseId: $courseId, title: $title) {
      session {
        id
        title
        isActive
        createdAt
      }
    }
  }
`;

const { mutate, loading } = useMutation(CREATE_SESSION_MUTATION);

async function handleCreate() {
  error.value = null;
  
  try {
    const result = await mutate({
      courseId: props.courseId,
      title: title.value
    });
    
    const sessionId = result?.data.whiteboardSessionCreate.session.id;
    router.push({ name: 'whiteboard', params: { id: sessionId } });
  } catch (e) {
    error.value = e as Error;
  }
}
</script>
```

---

### Add Strokes

```vue
<template>
  <div class="whiteboard-container">
    <canvas 
      ref="canvas" 
      @mousedown="startDrawing"
      @mousemove="draw"
      @mouseup="stopDrawing"
      @mouseleave="stopDrawing"
    ></canvas>
    
    <div class="tools">
      <button @click="clearCanvas">Clear</button>
      <input v-model="strokeColor" type="color" />
      <input v-model="strokeWidth" type="range" min="1" max="20" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

interface Props {
  sessionId: string;
}

const props = defineProps<Props>();

const canvas = ref<HTMLCanvasElement>();
const isDrawing = ref(false);
const strokeColor = ref('#000000');
const strokeWidth = ref(2);

let ctx: CanvasRenderingContext2D | null = null;
let currentStroke: Array<{x: number, y: number}> = [];

const ADD_STROKE_MUTATION = gql`
  mutation AddStroke($sessionId: ID!, $data: JSONString!) {
    whiteboardStrokeCreate(sessionId: $sessionId, data: $data) {
      stroke {
        id
        ts
      }
    }
  }
`;

const { mutate } = useMutation(ADD_STROKE_MUTATION);

onMounted(() => {
  if (canvas.value) {
    canvas.value.width = canvas.value.offsetWidth;
    canvas.value.height = canvas.value.offsetHeight;
    ctx = canvas.value.getContext('2d');
  }
});

function startDrawing(e: MouseEvent) {
  isDrawing.value = true;
  currentStroke = [];
  
  const rect = canvas.value!.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  
  currentStroke.push({ x, y });
}

function draw(e: MouseEvent) {
  if (!isDrawing.value || !ctx) return;
  
  const rect = canvas.value!.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  
  currentStroke.push({ x, y });
  
  // Draw on canvas
  ctx.strokeStyle = strokeColor.value;
  ctx.lineWidth = strokeWidth.value;
  ctx.lineCap = 'round';
  
  ctx.beginPath();
  const prev = currentStroke[currentStroke.length - 2];
  ctx.moveTo(prev.x, prev.y);
  ctx.lineTo(x, y);
  ctx.stroke();
}

async function stopDrawing() {
  if (!isDrawing.value) return;
  isDrawing.value = false;
  
  // Save stroke to backend
  if (currentStroke.length > 0) {
    try {
      await mutate({
        sessionId: props.sessionId,
        data: JSON.stringify({
          type: 'stroke',
          points: currentStroke,
          color: strokeColor.value,
          width: strokeWidth.value
        })
      });
    } catch (e) {
      console.error('Failed to save stroke:', e);
    }
  }
}

function clearCanvas() {
  if (ctx && canvas.value) {
    ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
  }
}
</script>
```

---

## Advanced Patterns

### Optimistic Updates

Update UI immediately before server responds:

```typescript
const { mutate } = useMutation(UPDATE_TICKET_MUTATION, {
  optimisticResponse: (vars) => ({
    supportTicketUpdate: {
      ticket: {
        __typename: 'SupportTicketType',
        id: vars.id,
        status: vars.status,
        updatedAt: new Date().toISOString()
      }
    }
  }),
  update: (cache, { data }) => {
    // Update cache manually if needed
    cache.modify({
      id: cache.identify({ __typename: 'SupportTicketType', id: vars.id }),
      fields: {
        status: () => data.supportTicketUpdate.ticket.status
      }
    });
  }
});
```

---

### Pagination

Handle paginated results (when implemented):

```typescript
const { result, fetchMore } = useQuery(ASSIGNMENTS_QUERY, {
  courseId: '1',
  limit: 10,
  offset: 0
});

async function loadMore() {
  await fetchMore({
    variables: {
      offset: result.value.assignments.length
    },
    updateQuery: (previousResult, { fetchMoreResult }) => {
      if (!fetchMoreResult) return previousResult;
      
      return {
        ...previousResult,
        assignments: [
          ...previousResult.assignments,
          ...fetchMoreResult.assignments
        ]
      };
    }
  });
}
```

---

### Real-time Updates with Polling

Poll for updates at regular intervals:

```typescript
const { result, loading, startPolling, stopPolling } = useQuery(MESSAGES_QUERY, {
  ticketId: '1'
}, {
  pollInterval: 5000 // Poll every 5 seconds
});

// Manually control polling
onMounted(() => {
  startPolling(3000); // Start polling every 3 seconds
});

onUnmounted(() => {
  stopPolling(); // Stop polling when component unmounts
});
```

---

### Error Recovery

Implement retry logic for failed requests:

```typescript
const { mutate, onError } = useMutation(CREATE_SUBMISSION_MUTATION);

onError((error) => {
  console.error('Mutation error:', error);
  
  // Show user-friendly error message
  if (error.message.includes('Authentication required')) {
    router.push('/login');
  } else if (error.message.includes('Network error')) {
    // Retry after delay
    setTimeout(() => {
      mutate(lastVariables);
    }, 2000);
  }
});
```

---

## Best Practices

1. **Always handle loading and error states** in your UI
2. **Use TypeScript types** from `@/shared/types/graphql.ts`
3. **Implement proper error messages** for users
4. **Use computed properties** for reactive data transformations
5. **Poll for updates** when real-time data is needed
6. **Clear Apollo cache** on logout
7. **Use fragments** for reusable field selections
8. **Implement optimistic updates** for better UX
9. **Add retry logic** for network errors
10. **Test with network throttling** to ensure good UX on slow connections

---

## Debugging Tips

1. **Use GraphiQL** interface at `/graphql/` to test queries
2. **Install Apollo DevTools** browser extension
3. **Enable debug logging** in Apollo Client:
   ```typescript
   const apolloClient = new ApolloClient({
     link: httpLink,
     cache: new InMemoryCache(),
     connectToDevTools: true // Enable in development
   });
   ```
4. **Log GraphQL errors** for debugging:
   ```typescript
   onError((error) => {
     console.error('[GraphQL Error]', {
       message: error.message,
       locations: error.graphQLErrors,
       path: error.path
     });
   });
   ```

---

For more information, see:
- [GraphQL API Documentation](./GRAPHQL_API.md)
- [Apollo Client Documentation](https://www.apollographql.com/docs/react/)
- [Vue Apollo Documentation](https://v4.apollo.vuejs.org/)


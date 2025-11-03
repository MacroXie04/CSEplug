import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

import { useAuthStore } from '@/features/auth/stores/auth';

export type AppRouteMeta = {
  requiresAuth?: boolean;
  guestOnly?: boolean;
  roles?: Array<'student' | 'teacher' | 'admin'>;
  title?: string;
};

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'login',
    component: () => import('@/features/auth/views/LoginView.vue'),
    meta: { guestOnly: true, title: 'Sign in' } satisfies AppRouteMeta
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/features/auth/views/ProfileView.vue'),
    meta: { requiresAuth: true, title: 'Profile' } satisfies AppRouteMeta
  },
  {
    path: '/student',
    component: () => import('@/shared/layouts/StudentLayout.vue'),
    meta: { requiresAuth: true, roles: ['student'], title: 'Student Portal' } satisfies AppRouteMeta,
    children: [
      {
        path: '',
        redirect: { name: 'student-dashboard' }
      },
      {
        path: 'dashboard',
        name: 'student-dashboard',
        component: () => import('@/features/dashboard/views/StudentDashboardView.vue'),
        meta: { title: 'Dashboard', requiresAuth: true, roles: ['student'] } satisfies AppRouteMeta
      },
      {
        path: 'courses/:id',
        name: 'student-course-detail',
        component: () => import('@/features/courses/views/CourseDetailView.vue'),
        props: true,
        meta: { requiresAuth: true, roles: ['student', 'teacher'] } satisfies AppRouteMeta
      },
      {
        path: 'assignments/:id',
        name: 'student-assignment-detail',
        component: () => import('@/features/assignments/views/AssignmentDetailView.vue'),
        props: true,
        meta: { requiresAuth: true, roles: ['student', 'teacher'] } satisfies AppRouteMeta
      },
      {
        path: 'notes',
        name: 'student-notes',
        component: () => import('@/features/notes/views/NotesView.vue'),
        meta: { requiresAuth: true, roles: ['student'] } satisfies AppRouteMeta
      },
      {
        path: 'whiteboard/:sessionId',
        name: 'student-whiteboard',
        component: () => import('@/features/whiteboard/views/WhiteboardView.vue'),
        props: true,
        meta: { requiresAuth: true, roles: ['student', 'teacher'] } satisfies AppRouteMeta
      },
      {
        path: 'support',
        name: 'student-support',
        component: () => import('@/features/support/views/SupportCenterView.vue'),
        meta: { requiresAuth: true, roles: ['student'] } satisfies AppRouteMeta
      }
    ]
  },
  {
    path: '/teacher',
    component: () => import('@/shared/layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true, roles: ['teacher', 'admin'], title: 'Teacher Portal' } satisfies AppRouteMeta,
    children: [
      {
        path: '',
        redirect: { name: 'teacher-dashboard' }
      },
      {
        path: 'dashboard',
        name: 'teacher-dashboard',
        component: () => import('@/features/dashboard/views/TeacherDashboardView.vue'),
        meta: { requiresAuth: true, roles: ['teacher', 'admin'] } satisfies AppRouteMeta
      },
      {
        path: 'courses/:id/assignments',
        name: 'teacher-course-assignments',
        component: () => import('@/features/assignments/views/TeacherAssignmentsView.vue'),
        props: true,
        meta: { requiresAuth: true, roles: ['teacher', 'admin'] } satisfies AppRouteMeta
      },
      {
        path: 'assignments/:id/submissions',
        name: 'teacher-assignment-submissions',
        component: () => import('@/features/assignments/views/TeacherSubmissionsView.vue'),
        props: true,
        meta: { requiresAuth: true, roles: ['teacher', 'admin'] } satisfies AppRouteMeta
      },
      {
        path: 'notes',
        name: 'teacher-notes',
        component: () => import('@/features/notes/views/TeacherNotesView.vue'),
        meta: { requiresAuth: true, roles: ['teacher', 'admin'] } satisfies AppRouteMeta
      },
      {
        path: 'whiteboard',
        name: 'teacher-whiteboard',
        component: () => import('@/features/whiteboard/views/TeacherWhiteboardView.vue'),
        meta: { requiresAuth: true, roles: ['teacher', 'admin'] } satisfies AppRouteMeta
      },
      {
        path: 'support',
        name: 'teacher-support',
        component: () => import('@/features/support/views/SupportCenterView.vue'),
        meta: { requiresAuth: true, roles: ['teacher', 'admin'] } satisfies AppRouteMeta
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/' 
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  const meta = (to.meta ?? {}) as AppRouteMeta;

  if (!auth.profileLoaded) {
    try {
      await auth.fetchProfile();
    } catch (error) {
      if (meta.requiresAuth) {
        return next({ name: 'login', query: { redirect: to.fullPath } });
      }
    }
  }

  if (meta.guestOnly && auth.isAuthenticated) {
    if (auth.role === 'teacher' || auth.role === 'admin') {
      return next({ name: 'teacher-dashboard' });
    }
    return next({ name: 'student-dashboard' });
  }

  if (meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }

  if (meta.roles && auth.role && !meta.roles.includes(auth.role)) {
    if (auth.role === 'teacher' || auth.role === 'admin') {
      return next({ name: 'teacher-dashboard' });
    }
    if (auth.role === 'student') {
      return next({ name: 'student-dashboard' });
    }
  }

  return next();
});

export default router;


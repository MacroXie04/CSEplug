/**
 * TypeScript type definitions for GraphQL schema
 * 
 * These types correspond to the GraphQL schema defined in the backend.
 * Keep these types in sync with the backend schema at:
 * src/graphql_api/schema.py
 */

// ============================================================================
// Core Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
}

// ============================================================================
// Course Types
// ============================================================================

export interface Course {
  id: string;
  title: string;
  description: string;
  syllabus: string;
  policy: string;
  startDate: string | null;
  endDate: string | null;
  createdAt: string;
  updatedAt: string;
}

export enum CourseMembershipRole {
  INSTRUCTOR = 'instructor',
  TEACHING_ASSISTANT = 'teaching_assistant',
  STUDENT = 'student'
}

export interface CourseMembership {
  id: string;
  course: Course;
  user: User;
  role: CourseMembershipRole;
  joinedAt: string;
}

// ============================================================================
// Assignment Types
// ============================================================================

export interface Assignment {
  id: string;
  course: Course;
  title: string;
  instructionsMd: string;
  instructionsHtml: string;
  points: number;
  publishAt: string | null;
  dueAt: string | null;
  createdAt: string;
  updatedAt: string;
  questions: AssignmentQuestion[];
  extensions: AssignmentExtension[];
}

export enum AssignmentQuestionType {
  FREE_RESPONSE = 'free_response',
  MULTIPLE_CHOICE = 'multiple_choice'
}

export interface AssignmentQuestion {
  id: string;
  assignment: Assignment;
  orderIndex: number;
  type: AssignmentQuestionType;
  weight: number;
  title: string;
  freeResponseQuestion: FreeResponseQuestion | null;
  multipleChoiceQuestion: MultipleChoiceQuestion | null;
}

export interface AssignmentExtension {
  id: string;
  assignment: Assignment;
  user: User;
  dueAt: string;
  createdAt: string;
}

// ============================================================================
// Question Types
// ============================================================================

export interface FreeResponseQuestion {
  id: string;
  course: Course;
  questionText: string;
  createdAt: string;
  updatedAt: string;
}

export interface MultipleChoiceQuestion {
  id: string;
  course: Course;
  questionText: string;
  createdAt: string;
  updatedAt: string;
  options: MultipleChoiceOption[];
}

export interface MultipleChoiceOption {
  id: string;
  question: MultipleChoiceQuestion;
  orderIndex: number;
  optionText: string;
  isCorrect: boolean;
}

// ============================================================================
// Submission & Grading Types
// ============================================================================

export interface Submission {
  id: string;
  user: User;
  assignmentQuestion: AssignmentQuestion;
  freeResponseText: string;
  multipleChoiceOption: MultipleChoiceOption | null;
  createdAt: string;
}

export interface SubmissionOutcome {
  id: string;
  submission: Submission;
  grader: User;
  score: number;
  feedbackMd: string;
  feedbackHtml: string;
  isEvaluated: boolean;
  updatedAt: string;
}

// ============================================================================
// Book Types
// ============================================================================

export interface Book {
  id: string;
  course: Course;
  title: string;
  description: string;
  createdAt: string;
  updatedAt: string;
}

export interface BookChapter {
  id: string;
  book: Book;
  orderIndex: number;
  title: string;
  markdownText: string;
  html: string;
  toc: string;
  createdAt: string;
  updatedAt: string;
}

// ============================================================================
// Asset & Deck Types
// ============================================================================

export interface Asset {
  id: string;
  uploader: User;
  course: Course | null;
  book: Book | null;
  name: string;
  type: string;
  url: string;
  thumbnailUrl: string;
  createdAt: string;
  updatedAt: string;
}

export interface Deck {
  id: string;
  course: Course;
  title: string;
  embedCode: string;
  createdAt: string;
  updatedAt: string;
}

// ============================================================================
// Notes Types
// ============================================================================

export interface NotesPage {
  id: string;
  course: Course;
  author: User;
  orderIndex: number;
  data: Record<string, any>;
  thumbnailSrc: string;
  thumbnailDarkSrc: string;
  createdAt: string;
  updatedAt: string;
  shapes: NotesShape[];
}

export interface NotesShape {
  id: string;
  page: NotesPage;
  data: Record<string, any>;
  version: number;
  createdAt: string;
}

// ============================================================================
// Whiteboard Types
// ============================================================================

export interface WhiteboardSession {
  id: string;
  course: Course;
  instructor: User;
  title: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface WhiteboardStroke {
  id: string;
  session: WhiteboardSession;
  user: User | null;
  data: Record<string, any>;
  ts: string;
}

// ============================================================================
// Support Types
// ============================================================================

export enum SupportTicketStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved'
}

export interface SupportTicket {
  id: string;
  requester: User;
  course: Course | null;
  subject: string;
  description: string;
  status: SupportTicketStatus;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
}

export interface ChatMessage {
  id: string;
  ticket: SupportTicket | null;
  course: Course | null;
  author: User;
  content: string;
  createdAt: string;
}

// ============================================================================
// GraphQL Response Types
// ============================================================================

export interface QueryResult<T> {
  data?: T;
  loading: boolean;
  error?: Error;
}

export interface MutationResult<T> {
  data?: T;
  loading: boolean;
  error?: Error;
}

// Common query responses
export interface MeQueryResponse {
  me: User | null;
}

export interface UserCoursesResponse {
  userCoursesConnection: CourseMembership[];
}

export interface CourseDetailResponse {
  course: Course;
}

export interface AssignmentsResponse {
  assignmentsConnection: Assignment[];
}

export interface AssignmentDetailResponse {
  assignment: Assignment;
}

export interface SubmissionsResponse {
  userSubmissions: Submission[];
}

export interface NotesResponse {
  notesPages: NotesPage[];
}

export interface WhiteboardSessionsResponse {
  whiteboardSessions: WhiteboardSession[];
}

export interface SupportTicketsResponse {
  supportTickets: SupportTicket[];
}

// Common mutation responses
export interface LoginMutationResponse {
  login: {
    user: User;
    success: boolean;
  };
}

export interface LogoutMutationResponse {
  logout: {
    success: boolean;
  };
}

export interface CourseCreateResponse {
  courseCreate: {
    course: Course;
  };
}

export interface AssignmentCreateResponse {
  assignmentCreate: {
    assignment: Assignment;
  };
}

export interface SubmissionCreateResponse {
  assignmentSubmissionCreate: {
    submission: Submission;
  };
}


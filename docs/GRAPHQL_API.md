# GraphQL API Documentation

This document provides comprehensive documentation for the CSEplug GraphQL API.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Queries](#queries)
  - [Health & Auth](#health--auth)
  - [Courses](#courses)
  - [Assignments](#assignments)
  - [Submissions](#submissions)
  - [Questions](#questions)
  - [Books](#books)
  - [Assets](#assets)
  - [Notes](#notes)
  - [Decks](#decks)
  - [Whiteboard](#whiteboard)
  - [Support](#support)
- [Mutations](#mutations)
  - [Authentication](#authentication-mutations)
  - [Courses](#course-mutations)
  - [Assignments](#assignment-mutations)
  - [Submissions & Grading](#submissions--grading-mutations)
  - [Questions](#question-mutations)
  - [Books](#book-mutations)
  - [Notes](#notes-mutations)
  - [Support](#support-mutations)
  - [Whiteboard](#whiteboard-mutations)
  - [Course Membership](#course-membership-mutations)
  - [Assets](#asset-mutations)
  - [Decks](#deck-mutations)

## Overview

The CSEplug GraphQL API is accessible at `/graphql/` endpoint. All requests should be made via HTTP POST with the GraphQL query in the request body.

**Endpoint:** `http://localhost:8000/graphql/` (development) or your production URL

**GraphiQL Interface:** Available at the same endpoint in browsers when `DEBUG=True`

## Authentication

Authentication is handled via JWT tokens stored in HTTP-only cookies. The authentication flow:

1. **Login**: Use the `login` mutation with email and password
2. **Token Storage**: Access and refresh tokens are automatically stored in cookies
3. **Authenticated Requests**: Tokens are automatically included in subsequent requests
4. **Token Refresh**: Use the `refresh` mutation to get a new access token
5. **Logout**: Use the `logout` mutation to invalidate tokens

Most queries and mutations require authentication. Unauthenticated requests will return a GraphQL error with message "Authentication required."

## Error Handling

GraphQL errors are returned in the `errors` array of the response:

```json
{
  "data": null,
  "errors": [
    {
      "message": "Course not found.",
      "locations": [{"line": 2, "column": 3}],
      "path": ["course"]
    }
  ]
}
```

Common error messages:
- `"Authentication required."` - User is not logged in
- `"Permission denied."` - User doesn't have required permissions
- `"Course not found."` - Requested resource doesn't exist
- `"You are not a member of this course."` - User doesn't have course access

---

## Queries

### Health & Auth

#### `ping`

Health check endpoint.

**Returns:** `String`

**Example:**
```graphql
query {
  ping
}
```

**Response:**
```json
{
  "data": {
    "ping": "pong"
  }
}
```

---

#### `me`

Get current authenticated user's profile.

**Returns:** `UserType`

**Authentication:** Required

**Example:**
```graphql
query {
  me {
    id
    email
    firstName
    lastName
  }
}
```

**Response:**
```json
{
  "data": {
    "me": {
      "id": "1",
      "email": "student@example.com",
      "firstName": "John",
      "lastName": "Doe"
    }
  }
}
```

---

### Courses

#### `userCoursesConnection`

Get all courses the current user is enrolled in or teaching.

**Returns:** `[CourseMembershipType]`

**Authentication:** Required

**Example:**
```graphql
query {
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
```

---

#### `course(id: ID!)`

Get detailed information about a specific course.

**Arguments:**
- `id` (ID!, required): Course ID

**Returns:** `CourseType`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  course(id: "1") {
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
}
```

---

#### `courseMemberships(courseId: ID)`

Get all memberships for a course (or all memberships if no courseId).

**Arguments:**
- `courseId` (ID, optional): Filter by course ID

**Returns:** `[CourseMembershipType]`

**Authentication:** Required

**Example:**
```graphql
query {
  courseMemberships(courseId: "1") {
    id
    role
    joinedAt
    user {
      id
      email
      firstName
      lastName
    }
    course {
      id
      title
    }
  }
}
```

---

### Assignments

#### `assignmentsConnection(courseId: ID)`

Get all assignments, optionally filtered by course.

**Arguments:**
- `courseId` (ID, optional): Filter by course ID

**Returns:** `[AssignmentType]`

**Authentication:** Required

**Example:**
```graphql
query {
  assignmentsConnection(courseId: "1") {
    id
    title
    instructionsMd
    points
    publishAt
    dueAt
    createdAt
    updatedAt
    questions {
      id
      type
      weight
      title
    }
  }
}
```

---

#### `assignment(id: ID!)`

Get detailed information about a specific assignment.

**Arguments:**
- `id` (ID!, required): Assignment ID

**Returns:** `AssignmentType`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  assignment(id: "1") {
    id
    title
    instructionsMd
    instructionsHtml
    points
    publishAt
    dueAt
    course {
      id
      title
    }
    questions {
      id
      orderIndex
      type
      weight
      title
      freeResponseQuestion {
        id
        questionText
      }
      multipleChoiceQuestion {
        id
        questionText
        options {
          id
          optionText
          isCorrect
        }
      }
    }
  }
}
```

---

#### `assignmentQuestion(id: ID!)`

Get details about a specific assignment question.

**Arguments:**
- `id` (ID!, required): Assignment question ID

**Returns:** `AssignmentQuestionType`

**Authentication:** Required

**Example:**
```graphql
query {
  assignmentQuestion(id: "1") {
    id
    type
    weight
    title
    freeResponseQuestion {
      id
      questionText
    }
  }
}
```

---

#### `assignmentExtensions(assignmentId: ID!)`

Get all deadline extensions for an assignment (instructors/TAs only).

**Arguments:**
- `assignmentId` (ID!, required): Assignment ID

**Returns:** `[AssignmentExtensionType]`

**Authentication:** Required

**Permissions:** Instructor or TA of the course

**Example:**
```graphql
query {
  assignmentExtensions(assignmentId: "1") {
    id
    user {
      id
      email
      firstName
      lastName
    }
    dueAt
    createdAt
  }
}
```

---

#### `userAssignmentExtension(assignmentId: ID!, userId: ID)`

Get deadline extension for a specific user (or current user if userId not provided).

**Arguments:**
- `assignmentId` (ID!, required): Assignment ID
- `userId` (ID, optional): User ID (requires instructor/TA permissions)

**Returns:** `AssignmentExtensionType`

**Authentication:** Required

**Example:**
```graphql
query {
  userAssignmentExtension(assignmentId: "1") {
    id
    dueAt
  }
}
```

---

### Submissions

#### `userSubmissions(assignmentQuestionId: ID)`

Get current user's submissions, optionally filtered by assignment question.

**Arguments:**
- `assignmentQuestionId` (ID, optional): Filter by assignment question

**Returns:** `[SubmissionType]`

**Authentication:** Required

**Example:**
```graphql
query {
  userSubmissions(assignmentQuestionId: "1") {
    id
    freeResponseText
    multipleChoiceOption {
      id
      optionText
    }
    createdAt
  }
}
```

---

#### `userSubmissionLatest(assignmentQuestionId: ID!)`

Get current user's most recent submission for a specific assignment question.

**Arguments:**
- `assignmentQuestionId` (ID!, required): Assignment question ID

**Returns:** `SubmissionType`

**Authentication:** Required

**Example:**
```graphql
query {
  userSubmissionLatest(assignmentQuestionId: "1") {
    id
    freeResponseText
    createdAt
  }
}
```

---

### Questions

#### `courseFreeResponseQuestionsConnection(courseId: ID!)`

Get all free response questions for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID

**Returns:** `[FreeResponseQuestionType]`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  courseFreeResponseQuestionsConnection(courseId: "1") {
    id
    questionText
    createdAt
    updatedAt
  }
}
```

---

#### `courseMultipleChoiceQuestionsConnection(courseId: ID!)`

Get all multiple choice questions for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID

**Returns:** `[MultipleChoiceQuestionType]`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  courseMultipleChoiceQuestionsConnection(courseId: "1") {
    id
    questionText
    options {
      id
      orderIndex
      optionText
      isCorrect
    }
    createdAt
    updatedAt
  }
}
```

---

### Books

#### `booksConnection(courseId: ID)`

Get all books, optionally filtered by course.

**Arguments:**
- `courseId` (ID, optional): Filter by course ID

**Returns:** `[BookType]`

**Example:**
```graphql
query {
  booksConnection(courseId: "1") {
    id
    title
    description
    createdAt
    updatedAt
  }
}
```

---

#### `book(id: ID!)`

Get detailed information about a specific book.

**Arguments:**
- `id` (ID!, required): Book ID

**Returns:** `BookType`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  book(id: "1") {
    id
    title
    description
    course {
      id
      title
    }
  }
}
```

---

#### `bookChapter(id: ID!)`

Get detailed information about a specific book chapter.

**Arguments:**
- `id` (ID!, required): Chapter ID

**Returns:** `BookChapterType`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  bookChapter(id: "1") {
    id
    title
    orderIndex
    markdownText
    html
    toc
    book {
      id
      title
    }
  }
}
```

---

### Assets

#### `courseAssets(courseId: ID!)`

Get all assets for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID

**Returns:** `[AssetType]`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  courseAssets(courseId: "1") {
    id
    name
    type
    url
    thumbnailUrl
    uploader {
      id
      email
      firstName
      lastName
    }
    createdAt
    updatedAt
  }
}
```

---

### Notes

#### `notesPages(courseId: ID!)`

Get all notes pages for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID

**Returns:** `[NotesPageType]`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  notesPages(courseId: "1") {
    id
    orderIndex
    data
    thumbnailSrc
    thumbnailDarkSrc
    author {
      id
      email
      firstName
      lastName
    }
    createdAt
    updatedAt
  }
}
```

---

#### `notesPage(id: ID!)`

Get detailed information about a specific notes page.

**Arguments:**
- `id` (ID!, required): Notes page ID

**Returns:** `NotesPageType`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  notesPage(id: "1") {
    id
    orderIndex
    data
    thumbnailSrc
    shapes {
      id
      data
      version
      createdAt
    }
  }
}
```

---

### Decks

#### `decksConnection(courseId: ID)`

Get all decks, optionally filtered by course.

**Arguments:**
- `courseId` (ID, optional): Filter by course ID

**Returns:** `[DeckType]`

**Example:**
```graphql
query {
  decksConnection(courseId: "1") {
    id
    title
    embedCode
    course {
      id
      title
    }
    createdAt
    updatedAt
  }
}
```

---

#### `deck(id: ID!)`

Get detailed information about a specific deck.

**Arguments:**
- `id` (ID!, required): Deck ID

**Returns:** `DeckType`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  deck(id: "1") {
    id
    title
    embedCode
    course {
      id
      title
    }
  }
}
```

---

### Whiteboard

#### `whiteboardSessions(courseId: ID)`

Get all whiteboard sessions, optionally filtered by course.

**Arguments:**
- `courseId` (ID, optional): Filter by course ID

**Returns:** `[WhiteboardSessionType]`

**Authentication:** Required

**Example:**
```graphql
query {
  whiteboardSessions(courseId: "1") {
    id
    title
    isActive
    instructor {
      id
      email
      firstName
      lastName
    }
    createdAt
    updatedAt
  }
}
```

---

#### `whiteboardSession(id: ID!)`

Get detailed information about a specific whiteboard session.

**Arguments:**
- `id` (ID!, required): Session ID

**Returns:** `WhiteboardSessionType`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  whiteboardSession(id: "1") {
    id
    title
    isActive
    course {
      id
      title
    }
    instructor {
      id
      email
    }
  }
}
```

---

#### `whiteboardStrokes(sessionId: ID!)`

Get all strokes for a whiteboard session.

**Arguments:**
- `sessionId` (ID!, required): Session ID

**Returns:** `[WhiteboardStrokeType]`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  whiteboardStrokes(sessionId: "1") {
    id
    data
    user {
      id
      email
    }
    ts
  }
}
```

---

### Support

#### `supportTickets(courseId: ID)`

Get all support tickets, optionally filtered by course.

**Arguments:**
- `courseId` (ID, optional): Filter by course ID

**Returns:** `[SupportTicketType]`

**Authentication:** Required

**Note:** Without courseId, returns only current user's tickets

**Example:**
```graphql
query {
  supportTickets(courseId: "1") {
    id
    subject
    description
    status
    requester {
      id
      email
      firstName
      lastName
    }
    createdAt
    updatedAt
    messages {
      id
      content
      author {
        id
        email
      }
      createdAt
    }
  }
}
```

---

#### `supportTicket(id: ID!)`

Get detailed information about a specific support ticket.

**Arguments:**
- `id` (ID!, required): Ticket ID

**Returns:** `SupportTicketType`

**Authentication:** Required

**Permissions:** Must be the requester or a course staff member

**Example:**
```graphql
query {
  supportTicket(id: "1") {
    id
    subject
    description
    status
    requester {
      id
      email
    }
    course {
      id
      title
    }
    messages {
      id
      content
      author {
        id
        email
      }
      createdAt
    }
  }
}
```

---

#### `courseChatMessages(courseId: ID!)`

Get all chat messages for a course (not associated with tickets).

**Arguments:**
- `courseId` (ID!, required): Course ID

**Returns:** `[ChatMessageType]`

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
query {
  courseChatMessages(courseId: "1") {
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
```

---

## Mutations

### Authentication Mutations

#### `login`

Authenticate user with email and password.

**Arguments:**
- `email` (String!, required): User email
- `password` (String!, required): User password

**Returns:**
```graphql
{
  user: UserType
  success: Boolean
}
```

**Example:**
```graphql
mutation {
  login(email: "student@example.com", password: "password123") {
    user {
      id
      email
      firstName
      lastName
    }
    success
  }
}
```

---

#### `refresh`

Refresh access token using refresh token from cookie.

**Returns:**
```graphql
{
  success: Boolean
}
```

**Example:**
```graphql
mutation {
  refresh {
    success
  }
}
```

---

#### `logout`

Logout and invalidate tokens.

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Example:**
```graphql
mutation {
  logout {
    success
  }
}
```

---

#### `updateProfile`

Update current user's profile information.

**Arguments:**
- `firstName` (String, optional): First name
- `lastName` (String, optional): Last name

**Returns:**
```graphql
{
  user: UserType
}
```

**Authentication:** Required

**Example:**
```graphql
mutation {
  updateProfile(firstName: "Jane", lastName: "Smith") {
    user {
      id
      email
      firstName
      lastName
    }
  }
}
```

---

### Course Mutations

#### `courseCreate`

Create a new course.

**Arguments:**
- `title` (String!, required): Course title
- `description` (String, optional): Course description
- `syllabus` (String, optional): Course syllabus
- `policy` (String, optional): Course policy
- `startDate` (Date, optional): Course start date
- `endDate` (Date, optional): Course end date

**Returns:**
```graphql
{
  course: CourseType
}
```

**Authentication:** Required

**Example:**
```graphql
mutation {
  courseCreate(
    title: "Introduction to Computer Science"
    description: "A comprehensive introduction to CS fundamentals"
    startDate: "2024-01-15"
    endDate: "2024-05-15"
  ) {
    course {
      id
      title
      description
      startDate
      endDate
    }
  }
}
```

---

#### `courseUpdate`

Update an existing course.

**Arguments:**
- `id` (ID!, required): Course ID
- `title` (String, optional): Course title
- `description` (String, optional): Course description
- `syllabus` (String, optional): Course syllabus
- `policy` (String, optional): Course policy
- `startDate` (Date, optional): Course start date
- `endDate` (Date, optional): Course end date

**Returns:**
```graphql
{
  course: CourseType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Example:**
```graphql
mutation {
  courseUpdate(
    id: "1"
    description: "Updated course description"
  ) {
    course {
      id
      title
      description
    }
  }
}
```

---

#### `courseDelete`

Delete a course.

**Arguments:**
- `id` (ID!, required): Course ID

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Example:**
```graphql
mutation {
  courseDelete(id: "1") {
    success
  }
}
```

---

### Assignment Mutations

#### `assignmentCreate`

Create a new assignment.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `title` (String!, required): Assignment title
- `instructionsMd` (String, optional): Instructions in Markdown
- `points` (Float, optional): Total points (default: 100)
- `publishAt` (DateTime, optional): Publish date/time
- `dueAt` (DateTime, optional): Due date/time

**Returns:**
```graphql
{
  assignment: AssignmentType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assignmentCreate(
    courseId: "1"
    title: "Homework 1"
    instructionsMd: "Complete the following problems..."
    points: 100
    dueAt: "2024-02-01T23:59:59Z"
  ) {
    assignment {
      id
      title
      points
      dueAt
    }
  }
}
```

---

#### `assignmentUpdate`

Update an existing assignment.

**Arguments:**
- `id` (ID!, required): Assignment ID
- `title` (String, optional): Assignment title
- `instructionsMd` (String, optional): Instructions in Markdown
- `points` (Float, optional): Total points
- `publishAt` (DateTime, optional): Publish date/time
- `dueAt` (DateTime, optional): Due date/time

**Returns:**
```graphql
{
  assignment: AssignmentType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assignmentUpdate(
    id: "1"
    dueAt: "2024-02-05T23:59:59Z"
  ) {
    assignment {
      id
      title
      dueAt
    }
  }
}
```

---

#### `assignmentDelete`

Delete an assignment.

**Arguments:**
- `id` (ID!, required): Assignment ID

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Example:**
```graphql
mutation {
  assignmentDelete(id: "1") {
    success
  }
}
```

---

#### `assignmentQuestionFreeResponseCreate`

Add a free response question to an assignment.

**Arguments:**
- `assignmentId` (ID!, required): Assignment ID
- `questionId` (ID!, required): Free response question ID
- `weight` (Float, optional): Question weight (default: 1)
- `orderIndex` (Int, optional): Display order (default: 0)
- `title` (String, optional): Question title

**Returns:**
```graphql
{
  assignmentQuestion: AssignmentQuestionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assignmentQuestionFreeResponseCreate(
    assignmentId: "1"
    questionId: "5"
    weight: 10
    orderIndex: 1
    title: "Problem 1"
  ) {
    assignmentQuestion {
      id
      type
      weight
      title
    }
  }
}
```

---

#### `assignmentQuestionMultipleChoiceCreate`

Add a multiple choice question to an assignment.

**Arguments:**
- `assignmentId` (ID!, required): Assignment ID
- `questionId` (ID!, required): Multiple choice question ID
- `weight` (Float, optional): Question weight (default: 1)
- `orderIndex` (Int, optional): Display order (default: 0)
- `title` (String, optional): Question title

**Returns:**
```graphql
{
  assignmentQuestion: AssignmentQuestionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assignmentQuestionMultipleChoiceCreate(
    assignmentId: "1"
    questionId: "3"
    weight: 5
    orderIndex: 0
  ) {
    assignmentQuestion {
      id
      type
      weight
    }
  }
}
```

---

#### `assignmentExtensionCreate`

Create or update a deadline extension for a student.

**Arguments:**
- `assignmentId` (ID!, required): Assignment ID
- `userId` (ID!, required): Student user ID
- `dueAt` (DateTime!, required): Extended due date/time

**Returns:**
```graphql
{
  extension: AssignmentExtensionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assignmentExtensionCreate(
    assignmentId: "1"
    userId: "10"
    dueAt: "2024-02-10T23:59:59Z"
  ) {
    extension {
      id
      user {
        id
        email
      }
      dueAt
    }
  }
}
```

---

### Submissions & Grading Mutations

#### `assignmentSubmissionCreate`

Create or update a submission for an assignment question.

**Arguments:**
- `assignmentQuestionId` (ID!, required): Assignment question ID
- `freeResponseText` (String, optional): Free response answer text
- `multipleChoiceOptionId` (ID, optional): Selected option ID for MC questions

**Returns:**
```graphql
{
  submission: SubmissionType
}
```

**Authentication:** Required

**Permissions:** Must be a member of the course

**Example:**
```graphql
mutation {
  assignmentSubmissionCreate(
    assignmentQuestionId: "1"
    freeResponseText: "My answer is..."
  ) {
    submission {
      id
      freeResponseText
      createdAt
    }
  }
}
```

---

#### `assignmentSubmissionOutcomeUpdate`

Update grading outcome for a submission.

**Arguments:**
- `submissionId` (ID!, required): Submission ID
- `score` (Float!, required): Score awarded
- `feedbackMd` (String, optional): Feedback in Markdown

**Returns:**
```graphql
{
  outcome: SubmissionOutcomeType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assignmentSubmissionOutcomeUpdate(
    submissionId: "5"
    score: 8.5
    feedbackMd: "Good work! Consider..."
  ) {
    outcome {
      id
      score
      feedbackMd
      isEvaluated
    }
  }
}
```

---

### Question Mutations

#### `courseFreeResponseQuestionCreate`

Create a new free response question in the question bank.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `questionText` (String!, required): Question text

**Returns:**
```graphql
{
  question: FreeResponseQuestionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  courseFreeResponseQuestionCreate(
    courseId: "1"
    questionText: "Explain the concept of recursion."
  ) {
    question {
      id
      questionText
      createdAt
    }
  }
}
```

---

#### `courseMultipleChoiceQuestionCreate`

Create a new multiple choice question in the question bank.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `questionText` (String!, required): Question text

**Returns:**
```graphql
{
  question: MultipleChoiceQuestionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  courseMultipleChoiceQuestionCreate(
    courseId: "1"
    questionText: "What is 2 + 2?"
  ) {
    question {
      id
      questionText
      createdAt
    }
  }
}
```

---

#### `courseMultipleChoiceOptionCreate`

Add an option to a multiple choice question.

**Arguments:**
- `questionId` (ID!, required): Multiple choice question ID
- `optionText` (String!, required): Option text
- `isCorrect` (Boolean, optional): Whether this is the correct answer (default: false)
- `orderIndex` (Int, optional): Display order (default: 0)

**Returns:**
```graphql
{
  option: MultipleChoiceOptionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  courseMultipleChoiceOptionCreate(
    questionId: "3"
    optionText: "4"
    isCorrect: true
    orderIndex: 0
  ) {
    option {
      id
      optionText
      isCorrect
    }
  }
}
```

---

### Book Mutations

#### `bookCreate`

Create a new book for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `title` (String!, required): Book title
- `description` (String, optional): Book description

**Returns:**
```graphql
{
  book: BookType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  bookCreate(
    courseId: "1"
    title: "Course Textbook"
    description: "Main course materials"
  ) {
    book {
      id
      title
      description
    }
  }
}
```

---

#### `bookChapterCreate`

Create a new chapter in a book.

**Arguments:**
- `bookId` (ID!, required): Book ID
- `title` (String!, required): Chapter title
- `markdownText` (String, optional): Chapter content in Markdown
- `orderIndex` (Int, optional): Display order (default: 0)

**Returns:**
```graphql
{
  chapter: BookChapterType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  bookChapterCreate(
    bookId: "1"
    title: "Chapter 1: Introduction"
    markdownText: "# Introduction\n\nWelcome to..."
    orderIndex: 1
  ) {
    chapter {
      id
      title
      orderIndex
    }
  }
}
```

---

### Notes Mutations

#### `notesPageCreate`

Create a new notes page for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `data` (JSONString, optional): Page data
- `thumbnailSrc` (String, optional): Thumbnail URL
- `thumbnailDarkSrc` (String, optional): Dark mode thumbnail URL

**Returns:**
```graphql
{
  page: NotesPageType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  notesPageCreate(
    courseId: "1"
    data: "{\"shapes\": []}"
  ) {
    page {
      id
      orderIndex
      createdAt
    }
  }
}
```

---

#### `notesPageDelete`

Delete a notes page.

**Arguments:**
- `id` (ID!, required): Notes page ID

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  notesPageDelete(id: "5") {
    success
  }
}
```

---

### Support Mutations

#### `supportTicketCreate`

Create a new support ticket.

**Arguments:**
- `courseId` (ID, optional): Course ID (if course-related)
- `subject` (String!, required): Ticket subject
- `description` (String!, required): Ticket description

**Returns:**
```graphql
{
  ticket: SupportTicketType
}
```

**Authentication:** Required

**Example:**
```graphql
mutation {
  supportTicketCreate(
    courseId: "1"
    subject: "Cannot access assignment"
    description: "I'm getting an error when trying to view Assignment 2..."
  ) {
    ticket {
      id
      subject
      status
      createdAt
    }
  }
}
```

---

#### `supportTicketUpdate`

Update a support ticket's status.

**Arguments:**
- `id` (ID!, required): Ticket ID
- `status` (String, optional): New status (open, in_progress, resolved)

**Returns:**
```graphql
{
  ticket: SupportTicketType
}
```

**Authentication:** Required

**Permissions:** Must be the requester or course staff

**Example:**
```graphql
mutation {
  supportTicketUpdate(
    id: "3"
    status: "resolved"
  ) {
    ticket {
      id
      status
      updatedAt
    }
  }
}
```

---

#### `chatMessageCreate`

Create a chat message in a ticket or course chat.

**Arguments:**
- `ticketId` (ID, optional): Support ticket ID
- `courseId` (ID, optional): Course ID (for course chat)
- `content` (String!, required): Message content

**Note:** Either ticketId or courseId must be provided

**Returns:**
```graphql
{
  message: ChatMessageType
}
```

**Authentication:** Required

**Example:**
```graphql
mutation {
  chatMessageCreate(
    ticketId: "3"
    content: "Thank you for your help!"
  ) {
    message {
      id
      content
      createdAt
    }
  }
}
```

---

### Whiteboard Mutations

#### `whiteboardSessionCreate`

Create a new whiteboard session for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `title` (String!, required): Session title

**Returns:**
```graphql
{
  session: WhiteboardSessionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  whiteboardSessionCreate(
    courseId: "1"
    title: "Lecture 5 - Data Structures"
  ) {
    session {
      id
      title
      isActive
      createdAt
    }
  }
}
```

---

#### `whiteboardSessionUpdate`

Update a whiteboard session.

**Arguments:**
- `id` (ID!, required): Session ID
- `title` (String, optional): Session title
- `isActive` (Boolean, optional): Whether session is active

**Returns:**
```graphql
{
  session: WhiteboardSessionType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  whiteboardSessionUpdate(
    id: "1"
    isActive: false
  ) {
    session {
      id
      isActive
    }
  }
}
```

---

#### `whiteboardSessionDelete`

Delete a whiteboard session.

**Arguments:**
- `id` (ID!, required): Session ID

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Example:**
```graphql
mutation {
  whiteboardSessionDelete(id: "1") {
    success
  }
}
```

---

#### `whiteboardStrokeCreate`

Add a stroke to a whiteboard session.

**Arguments:**
- `sessionId` (ID!, required): Session ID
- `data` (JSONString!, required): Stroke data

**Returns:**
```graphql
{
  stroke: WhiteboardStrokeType
}
```

**Authentication:** Required

**Permissions:** Must be a member of the course; session must be active

**Example:**
```graphql
mutation {
  whiteboardStrokeCreate(
    sessionId: "1"
    data: "{\"type\": \"line\", \"points\": [...]}"
  ) {
    stroke {
      id
      ts
    }
  }
}
```

---

### Course Membership Mutations

#### `courseMembershipAdd`

Add a user to a course or update their role.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `userEmail` (String!, required): User's email address
- `role` (String!, required): Role (instructor, teaching_assistant, student)

**Returns:**
```graphql
{
  membership: CourseMembershipType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Example:**
```graphql
mutation {
  courseMembershipAdd(
    courseId: "1"
    userEmail: "student@example.com"
    role: "student"
  ) {
    membership {
      id
      role
      user {
        id
        email
      }
    }
  }
}
```

---

#### `courseMembershipRemove`

Remove a user from a course.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `userId` (ID!, required): User ID to remove

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Note:** Cannot remove the last instructor

**Example:**
```graphql
mutation {
  courseMembershipRemove(
    courseId: "1"
    userId: "10"
  ) {
    success
  }
}
```

---

#### `courseMembershipUpdateRole`

Update a user's role in a course.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `userId` (ID!, required): User ID
- `role` (String!, required): New role (instructor, teaching_assistant, student)

**Returns:**
```graphql
{
  membership: CourseMembershipType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Note:** Cannot change role if it would leave no instructors

**Example:**
```graphql
mutation {
  courseMembershipUpdateRole(
    courseId: "1"
    userId: "10"
    role: "teaching_assistant"
  ) {
    membership {
      id
      role
      user {
        id
        email
      }
    }
  }
}
```

---

### Asset Mutations

#### `assetCreate`

Upload a new asset to a course or book.

**Arguments:**
- `courseId` (ID, optional): Course ID
- `bookId` (ID, optional): Book ID
- `name` (String!, required): Asset name
- `type` (String!, required): Asset type
- `url` (String!, required): Asset URL
- `thumbnailUrl` (String, optional): Thumbnail URL

**Note:** Either courseId or bookId must be provided

**Returns:**
```graphql
{
  asset: AssetType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assetCreate(
    courseId: "1"
    name: "Lecture Slides Week 1"
    type: "pdf"
    url: "https://example.com/slides.pdf"
  ) {
    asset {
      id
      name
      url
      createdAt
    }
  }
}
```

---

#### `assetDelete`

Delete an asset.

**Arguments:**
- `id` (ID!, required): Asset ID

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  assetDelete(id: "5") {
    success
  }
}
```

---

### Deck Mutations

#### `deckCreate`

Create a new presentation deck for a course.

**Arguments:**
- `courseId` (ID!, required): Course ID
- `title` (String!, required): Deck title
- `embedCode` (String, optional): Embed code for the deck

**Returns:**
```graphql
{
  deck: DeckType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  deckCreate(
    courseId: "1"
    title: "Week 1 Slides"
    embedCode: "<iframe src='...'></iframe>"
  ) {
    deck {
      id
      title
      createdAt
    }
  }
}
```

---

#### `deckUpdate`

Update a deck's information.

**Arguments:**
- `id` (ID!, required): Deck ID
- `title` (String, optional): Deck title
- `embedCode` (String, optional): Embed code

**Returns:**
```graphql
{
  deck: DeckType
}
```

**Authentication:** Required

**Permissions:** Must be an instructor or TA of the course

**Example:**
```graphql
mutation {
  deckUpdate(
    id: "1"
    title: "Week 1 Slides (Updated)"
  ) {
    deck {
      id
      title
      updatedAt
    }
  }
}
```

---

#### `deckDelete`

Delete a deck.

**Arguments:**
- `id` (ID!, required): Deck ID

**Returns:**
```graphql
{
  success: Boolean
}
```

**Authentication:** Required

**Permissions:** Must be an instructor of the course

**Example:**
```graphql
mutation {
  deckDelete(id: "1") {
    success
  }
}
```

---

## Best Practices

1. **Always include error handling** in your client code
2. **Use fragments** for reusable field selections
3. **Batch queries** when fetching related data
4. **Use variables** instead of string interpolation for arguments
5. **Specify only the fields you need** to minimize payload size
6. **Cache results** appropriately on the client side
7. **Handle authentication errors** and redirect to login when needed
8. **Use optimistic UI updates** for better UX with mutations

## Rate Limiting

Currently, there is no rate limiting implemented. However, please be respectful of the API and avoid making excessive requests.

## Support

For API issues or questions:
- Check the GraphiQL interface at `/graphql/` for interactive documentation
- Review the backend schema at `src/graphql_api/schema.py`
- File an issue in the project repository


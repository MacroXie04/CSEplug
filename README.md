# CSE Plug — Computer Science Education Platform

CSE Plug is a full-stack educational platform for computer science courses, featuring assignment management, collaborative whiteboards, lecture notes, and comprehensive grading tools.

## Architecture

- **Backend**: Django 4.2 + GraphQL (Graphene-Django) + Django Channels (WebSocket)
- **Student Frontend**: Vue 3 + Vite + Apollo Client
- **Teacher Frontend**: React 18 + Vite + Apollo Client
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Cache & WebSocket**: Redis
- **Deployment**: Docker + docker-compose + Nginx

## Repository Structure

```
cse-plug/
├── src/                      # Django backend
│   ├── core/                 # Project settings
│   ├── accounts/             # User authentication (email-based)
│   ├── courses/              # Course & membership management
│   ├── assignments/          # Assignment & questions
│   ├── submissions/          # Student submissions
│   ├── grading/              # Grading outcomes
│   ├── questions/            # Question bank (MCQ + free response)
│   ├── books/                # Course books & chapters
│   ├── assets/               # Course/book media assets
│   ├── notes/                # Collaborative notes pages
│   ├── decks/                # Slide decks
│   ├── whiteboard/           # Real-time whiteboard
│   ├── support/              # Support tickets & chat
│   └── graphql_api/          # GraphQL schema & mutations
├── frontend/
│   ├── app/                  # Vue 3 student interface
│   └── admin/                # React 18 teacher/TA interface
├── nginx/                    # Reverse proxy configuration
└── docker-compose.yml        # Container orchestration

```

## Features

### For Students (Vue App)
- View enrolled courses and assignments
- Submit answers (markdown for free response, select for MCQ)
- Read course books and chapters
- View lecture notes and whiteboard sessions
- Check grades and feedback
- Support center with tickets and chat

### For Teachers & TAs (React App)
- Create and manage courses
- Build question banks (free response + multiple choice)
- Create assignments with weighted questions
- Grade submissions with markdown feedback
- Auto-grade MCQ submissions
- Manage course books and chapters
- Control collaborative whiteboard sessions
- Create and export notes pages

### For Administrators (Django Admin)
- Full user management
- Course creation and enrollment
- Database maintenance
- System configuration

## Data Model

### Core Entities
- **User**: Email-based authentication
- **Course**: Title, syllabus, policy, dates
- **CourseMembership**: Links users to courses with roles (Instructor, TA, Student)
- **Assignment**: Instructions (markdown/HTML), publish/due dates, total points
- **AssignmentQuestion**: Links assignments to question bank with weights and ordering
- **FreeResponseQuestion**: Open-ended question in course question bank
- **MultipleChoiceQuestion**: MCQ with multiple options
- **Submission**: Student answer to an assignment question
- **SubmissionOutcome**: Grade, feedback, evaluation status
- **Book & BookChapter**: Structured course reading material
- **Asset**: Course/book images and videos
- **NotesPage**: Collaborative lecture notes with shapes
- **WhiteboardSession & WhiteboardStroke**: Real-time drawing sessions
- **Deck**: Embedded slide presentations

## GraphQL API

### Queries
- `me`: Current user profile
- `userCoursesConnection`: User's enrolled courses with membership roles
- `course(id)`, `courseMemberships(courseId)`
- `assignmentsConnection(courseId)`, `assignment(id)`, `assignmentQuestion(id)`
- `userAssignmentsConnection`, `userAssignment(id)`, `userAssignmentQuestion(id)`
- `courseFreeResponseQuestionsConnection(courseId)`
- `courseMultipleChoiceQuestionsConnection(courseId)`
- `userSubmissions(assignmentQuestionId)`, `userSubmissionLatest(assignmentQuestionId)`
- `booksConnection(courseId)`, `book(id)`, `bookChapter(id)`
- `courseAssets(courseId)`
- `notesPages(courseId)`, `notesPage(id)`
- `decksConnection(courseId)`, `deck(id)`

### Mutations
- **Auth**: `login`, `refresh`, `logout`, `updateProfile`
- **Courses**: `courseCreate`, `courseUpdate`, `courseDelete`
- **Assignments**: `assignmentCreate/Update/Delete`, `assignmentQuestionFreeResponseCreate`, `assignmentQuestionMultipleChoiceCreate`
- **Questions**: `courseFreeResponseQuestionCreate`, `courseMultipleChoiceQuestionCreate`, `courseMultipleChoiceOptionCreate`
- **Submissions**: `assignmentSubmissionCreate`, `assignmentSubmissionOutcomeUpdate`
- **Books**: `bookCreate`, `bookChapterCreate`
- **Notes**: `notesPageCreate`, `notesPageDelete`

### Subscriptions (Coming Soon)
- `assignmentSubmissionUpdated(submissionId)`
- `notesPageListUpdated(courseId)`
- `notesPageUpdated(notesPageId)`
- `notesPageShapesUpdated(notesPageId)`

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 20+
- Redis (for Channels)

### Backend Setup

```bash
cd src
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The backend will be available at `http://localhost:8000`.
- GraphQL endpoint: `http://localhost:8000/graphql`
- Django Admin: `http://localhost:8000/admin/`

### Frontend Setup

#### Vue Student App

```bash
cd frontend/app
npm install
npm run dev
```

Student app runs at `http://localhost:5173`

#### React Teacher App

```bash
cd frontend/admin
npm install
npm run dev
```

Teacher app runs at `http://localhost:5174`

### Docker Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration

# Start all services
docker-compose up
```

Services:
- Backend: `http://localhost:8000`
- Student frontend: `http://localhost:5173`
- Teacher frontend: `http://localhost:5174`
- Nginx (unified): `http://localhost`
- Redis: `localhost:6379`

## Authentication

- JWT tokens stored in HttpOnly cookies
- Access token: 15 minutes
- Refresh token: 7 days
- Login via email and password

## Development

### Create a Superuser

```bash
cd src
python manage.py createsuperuser
```

### Add Sample Data

1. Login to Django Admin (`/admin/`)
2. Create courses
3. Add course memberships (assign instructors, TAs, students)
4. Create question banks
5. Create assignments and link questions

## API Testing

Access GraphiQL interface at `http://localhost:8000/graphql`

Example query:
```graphql
query {
  me {
    id
    email
    firstName
    lastName
  }
  userCoursesConnection {
    role
    course {
      title
    }
  }
}
```

Example mutation:
```graphql
mutation {
  login(email: "student@example.com", password: "password") {
    user {
      email
      firstName
    }
    success
  }
}
```

## Deployment

For production deployment:
1. Set `DJANGO_DEBUG=False`
2. Configure PostgreSQL database
3. Set strong `DJANGO_SECRET_KEY`
4. Configure allowed hosts
5. Use production-grade WSGI server (gunicorn/uvicorn)
6. Enable HTTPS with SSL certificates
7. Configure S3 for media uploads

## License

This project is licensed under the terms specified in the LICENSE file.

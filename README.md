# CSE Plug — Computer Science Education Platform

CSE Plug is a monorepo project that delivers a full-stack learning experience for computer science courses. The platform combines a Django backend (REST + GraphQL + Channels) with a Vue 3 frontend for both students and teachers. Administrators manage the system through Django’s built-in admin site.

## Repository Layout

```
cse-plug/
├── src/                   # Django backend
│   ├── core/              # Project configuration
│   ├── accounts/          # Authentication & roles
│   ├── courses/           # Course management
│   ├── assignments/       # Assignment flow
│   ├── notes/             # Lecture notes
│   ├── whiteboard/        # Real-time whiteboard
│   ├── support/           # Support & chat
│   └── graphql_api/       # GraphQL schema
├── frontend/              # Vue application for students & teachers
│   └── app/
├── nginx/                 # Reverse proxy configuration
│   └── default.conf
├── docker-compose.yml     # Local orchestration
└── README.md
```

## Getting Started

1. Clone the repository and create a virtual environment for Django.
2. Duplicate your environment template to `.env` and populate necessary keys.
3. Install backend dependencies and run migrations.
4. Install frontend dependencies under `frontend/app` and start the development server.
5. Optionally run `docker-compose up` to start all services (backend, frontend, Redis, Nginx) together.

Detailed setup documentation will be added as the implementation progresses.

# DockerForge Web UI

A modern web-based user interface for DockerForge, providing a comprehensive Docker management experience.

## Architecture

The DockerForge Web UI follows an API-First approach with:

- **Backend**: FastAPI for high-performance API endpoints
- **Frontend**: Vue.js with Vuetify for a responsive, modern UI

## Directory Structure

```
src/web/
├── api/                # FastAPI backend
│   ├── main.py         # Main application entry point
│   ├── requirements.txt # Backend dependencies
│   ├── routers/        # API route handlers
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   └── services/       # Business logic
│
└── frontend/           # Vue.js frontend
    ├── public/         # Static assets
    ├── src/            # Source code
    │   ├── main.js     # Application entry point
    │   ├── App.vue     # Root component
    │   ├── router.js   # Vue Router configuration
    │   ├── store.js    # Vuex store configuration
    │   ├── components/ # Reusable components
    │   └── views/      # Page components
    └── package.json    # Frontend dependencies
```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker and Docker Compose

### Backend Setup

```bash
# Navigate to the API directory
cd src/web/api

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload --host 0.0.0.0 --port 54321
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd src/web/frontend

# Install dependencies
npm install

# Run the development server
npm run serve
```

### Docker Setup

You can also run the entire application using Docker Compose:

```bash
# From the project root
docker-compose up
```

This will start the backend, frontend, PostgreSQL database, and Redis cache.

## API Documentation

Once the backend is running, you can access the API documentation at:

- Swagger UI: http://localhost:54321/docs
- ReDoc: http://localhost:54321/redoc

## Features

- **Dashboard**: Overview of Docker system and resources
- **Container Management**: Create, start, stop, and manage containers
- **Image Management**: Pull, build, and manage images
- **Volume & Network Management**: Create and manage volumes and networks
- **Compose Management**: Manage Docker Compose files
- **Security**: Vulnerability scanning and security auditing
- **Backup & Restore**: Backup and restore containers, images, and volumes
- **Monitoring**: Resource monitoring and log analysis
- **User Management**: Authentication and authorization

## Implementation Status

This is a work in progress. The implementation is following the plan outlined in `docs/project_plans/web_ui_implementation.md`.

- [x] Project setup
- [x] Basic application structure
- [ ] API endpoints
- [ ] Database models
- [ ] Authentication
- [ ] Frontend components
- [ ] Integration with DockerForge core

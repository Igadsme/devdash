# DevDash - Developer Productivity Tracker

A comprehensive full-stack developer productivity dashboard built with Python FastAPI backend and vanilla JavaScript frontend.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Task Management**: Create, update, and track tasks with priority levels
- **Pomodoro Timer**: Built-in timer for focused work sessions
- **GitHub Integration**: Track coding activity and statistics
- **AI Insights**: Get productivity insights and recommendations
- **Analytics Dashboard**: Visual charts and productivity metrics
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- JWT Authentication
- Pydantic (Data validation)

### Frontend
- Vanilla JavaScript
- HTML5/CSS3
- Tailwind CSS
- Chart.js for analytics
- Lucide icons

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd devdash
```

2. **Install Python dependencies**
```bash
pip install -r devdash-requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```
DATABASE_URL=postgresql://username:password@localhost:5432/devdash
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
PORT=8000
```

4. **Set up the database**
Make sure PostgreSQL is running and create a database named `devdash`.

5. **Run the application**
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Project Structure

```
devdash/
├── main.py                 # Main FastAPI application
├── models.py              # SQLAlchemy database models
├── database.py            # Database configuration
├── auth_utils.py          # Authentication utilities
├── routers/               # API route modules
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── tasks.py          # Task management routes
│   ├── pomodoro.py       # Pomodoro timer routes
│   ├── github.py         # GitHub statistics routes
│   └── insights.py       # AI insights routes
├── static/               # Frontend files
│   ├── index.html        # Main HTML file
│   └── app.js           # JavaScript application
├── devdash-requirements.txt  # Python dependencies
└── README.md            # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Tasks
- `GET /api/tasks/` - Get user tasks
- `POST /api/tasks/` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Pomodoro
- `GET /api/pomodoro/sessions` - Get pomodoro sessions
- `POST /api/pomodoro/sessions` - Create new session
- `PUT /api/pomodoro/sessions/{id}` - Update session

### GitHub Stats
- `GET /api/github/stats` - Get GitHub statistics
- `POST /api/github/sync` - Sync GitHub data

### AI Insights
- `GET /api/insights/` - Get insights
- `POST /api/insights/generate` - Generate new insights

### Dashboard
- `GET /api/dashboard-stats` - Get dashboard statistics

## Development

To run in development mode with auto-reload:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Database Models

- **User**: User accounts and profiles
- **Task**: User tasks with priorities and deadlines
- **PomodoroSession**: Pomodoro timer sessions
- **GitHubStats**: GitHub activity statistics
- **AIInsight**: AI-generated productivity insights

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

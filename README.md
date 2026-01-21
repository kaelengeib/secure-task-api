# Secure Task API

A REST API for managing personal tasks with user authentication and authorization. Built with Flask, SQLite, and bcrypt for secure password hashing.

## Features

- User registration and authentication
- Token-based authorization
- Password hashing with bcrypt
- Full CRUD operations for tasks
- Users can only access their own tasks
- Input validation and SQL injection protection

## Tech Stack

- **Python 3** - Programming language
- **Flask** - Web framework
- **SQLite** - Database
- **bcrypt** - Password hashing
- **REST API** - Architecture pattern

## Setup Instructions

1. Clone the repository
2. Create virtual environment:
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Mac/Linux
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Initialize database:
```bash
   python database.py
```
5. Run the application:
```bash
   python app.py
```

The API will be available at `http://127.0.0.1:5000`

## API Endpoints

### Authentication

**Register a new user**
```
POST /register
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Login**
```
POST /login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

Returns: { "token": "auth_token_here" }
```

### Tasks (Authentication Required)

Include token in header: `Authorization: your_token_here`

**Get all tasks**
```
GET /tasks
```

**Create a task**
```
POST /tasks
Content-Type: application/json

{
  "title": "Task title",
  "description": "Optional description"
}
```

**Update a task**
```
PUT /tasks/<task_id>
Content-Type: application/json

{
  "title": "Updated title",
  "completed": true
}
```

**Delete a task**
```
DELETE /tasks/<task_id>
```

## Security Features

- Passwords hashed with bcrypt before storage
- Token-based authentication
- Parameterized SQL queries prevent SQL injection
- Input validation on all endpoints
- Users can only access their own tasks

## Testing

Run the test script to verify all endpoints:
```bash
python test.py
```

from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import secrets
from contextlib import contextmanager

app = Flask(__name__)

# Store active sessions
active_sessions = {}

@contextmanager
def get_db():
    conn = sqlite3.connect('tasks.db', timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def require_auth():
    """Check if request has valid auth token, return user_id or None"""
    token = request.headers.get('Authorization')
    
    if not token:
        return None
    
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]
    
    return active_sessions.get(token)

# Test endpoint
@app.route('/')
def home():
	return jsonify({"message": "Task API is running"})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                          (username, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
        
        return jsonify({"message": "User created", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    username = data['username']
    password = data['password']
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        token = secrets.token_hex(16)
        active_sessions[token] = user['id']
        
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        tasks = cursor.fetchall()
    
    task_list = [dict(task) for task in tasks]
    
    return jsonify({"tasks": task_list}), 200


@app.route('/tasks', methods=['POST'])
def create_task():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    title = data['title'].strip()
    description = data.get('description', '').strip()
    
    if len(title) == 0:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)',
                      (user_id, title, description))
        conn.commit()
        task_id = cursor.lastrowid
    
    return jsonify({"message": "Task created", "task_id": task_id}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if task exists and belongs to user
    cursor.execute('SELECT id FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    
    # Update task
    title = data.get('title')
    description = data.get('description')
    completed = data.get('completed')
    
    updates = []
    params = []
    
    if title is not None:
        updates.append('title = ?')
        params.append(title)
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if completed is not None:
        updates.append('completed = ?')
        params.append(1 if completed else 0)
    
    if updates:
        params.append(task_id)
        params.append(user_id)
        cursor.execute(f'UPDATE tasks SET {", ".join(updates)} WHERE id = ? AND user_id = ?', params)
        conn.commit()
    
    conn.close()
    
    return jsonify({"message": "Task updated"}), 200


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    
    conn.close()
    
    return jsonify({"message": "Task deleted"}), 200

if __name__ == '__main__':
	app.run(debug=True, port=5000)
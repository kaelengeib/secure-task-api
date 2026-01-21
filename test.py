import requests

BASE_URL = 'http://127.0.0.1:5000'

# 1. Register a user
print("1. Registering user...")
response = requests.post(f'{BASE_URL}/register', json={'username': 'kaelen', 'password': 'test123'})
print(response.json())

# 2. Login
print("\n2. Logging in...")
response = requests.post(f'{BASE_URL}/login', json={'username': 'kaelen', 'password': 'test123'})
login_data = response.json()
print(login_data)

token = login_data.get('token')
headers = {'Authorization': token}

# 3. Create a task
print("\n3. Creating task...")
response = requests.post(f'{BASE_URL}/tasks', 
                        headers=headers,
                        json={'title': 'Finish resume projects', 'description': 'Build task API'})
print(response.json())

# 4. Get all tasks
print("\n4. Getting all tasks...")
response = requests.get(f'{BASE_URL}/tasks', headers=headers)
print(response.json())

# 5. Update task
print("\n5. Updating task...")
response = requests.put(f'{BASE_URL}/tasks/1', 
                       headers=headers,
                       json={'completed': True})
print(response.json())

# 6. Get tasks again
print("\n6. Getting tasks after update...")
response = requests.get(f'{BASE_URL}/tasks', headers=headers)
print(response.json())

print("\n✅ All endpoints working!")
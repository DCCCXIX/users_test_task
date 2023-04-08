from flask import Flask, request
from flask.json import jsonify
import csv

app = Flask(__name__)

def read_csv_file():
    """Helper function to read csv files"""
    try:
        with open('users.csv', mode='r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        # if table is not found - create an empty table
        write_csv_file(None)

def write_csv_file(users):
    """Helper function to write csv files"""
    fieldnames = ['id', 'name', 'age', 'city']
    with open('users.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        if users:
            # so we don't write rows while creating an empty table
            writer.writerows(users)

def generate_user_id(users):
    """Helper function to generate user IDs"""
    ids = [int(user['id']) for user in users]
    return max(ids) + 1 if ids else 1

def validate_user_data(user):
    """User data validation"""
    try:
        if "name" in user: assert isinstance(user.get("name"), str) and len(user.get("name")) < 50
        if "age" in user: assert isinstance(user.get("age"), int) and user.get("age") > 0
        if "city" in user: assert isinstance(user.get("city"), str) and len(user.get("city")) < 50
    except AssertionError:
        return False    
    return True

@app.route('/users', methods=['GET'])
def get_users():
    """Returns user list by name or city"""
    users = read_csv_file()
    name = request.args.get('name')
    city = request.args.get('city')
    if name or city:
        filtered_users = []
        for user in users:
            if (name and user['name'] == name) or (city and user['city'] == city):
                filtered_users.append(user)
        return {'users': filtered_users}, 200
    else:
        return {'users': users}, 200

@app.route('/users', methods=['POST'])
def add_user():
    """Adds a user to the existing table"""    
    user = request.get_json()
    
    if not validate_user_data(user):
        return {'error': 'Invalid user data'}, 400
    users = read_csv_file()    
    user['id'] = generate_user_id(users)
    users.append(user)
    write_csv_file(users)
    return {'user': user}, 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def change_user(user_id):
    """Change user info"""
    user = request.get_json()
    if not validate_user_data(user):
        return {'error': 'Invalid user data'}, 400
    users = read_csv_file()
    updated_user = next((u for u in users if int(u['id']) == user_id), None)
    if updated_user:
        updated_user.update({key: value for key, value in user.items() if key in updated_user})
        write_csv_file(users)        
        return {'user': updated_user}, 201
    else:
        return {'error': 'User not found'}, 404

if __name__ == '__main__':
    app.run(debug=True)
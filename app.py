from flask import Flask, request
from flask.json import jsonify
import csv
import re
import pandas as pd

app = Flask(__name__)


def read_csv_file() -> list:
    """
    Reads a CSV file containing user data.

    Returns:
        list: A list of dictionaries, where each dictionary represents a user's data
            with keys as column names and values as corresponding values from the CSV file.
    Raises:
        FileNotFoundError: If the CSV file is not found, a new empty table is created by calling write_csv_file() function,
            and then the file is read again.
    """
    with open('users.csv', mode='r') as file:  
        try:                  
            reader = csv.DictReader(file)
        except FileNotFoundError:            
            write_csv_file(None) # if table is not found - create an empty table
            reader = csv.DictReader(file)
        return list(reader)
    

def write_csv_file(users: list) -> None:
    """
    Writes user data to a CSV file.

    Args:
        users (list): A list of dictionaries, where each dictionary represents a user's data
            with keys as column names and values as corresponding values.

    Note:
        If the users list is empty, the function will create an empty table with only the header row
        to represent an empty CSV file.
    """
    fieldnames = ['id', 'name', 'age', 'city', 'date', 'rating']
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        if users: # so we don't write rows while creating an empty table            
            writer.writerows(users)


def generate_user_id(users: list) -> int:
    """
    Generates a unique user ID based on the existing list of users.

    Args:
        users (list): A list of dictionaries, where each dictionary represents a user's data
            with keys as column names and values as corresponding values.

    Returns:
        int: A unique user ID that is one greater than the maximum user ID found in the existing users list.
            If the users list is empty, the function returns 1 as the initial user ID.
    """
    ids = [int(user['id']) for user in users]
    return max(ids) + 1 if ids else 1 # return id if the table was empty prior to user addition


def validate_user_data(user: dict) -> bool:
    """
    Validates user data to ensure it meets the expected format and constraints.

    Args:
        user (dict): A dictionary representing user data with keys as column names and values as corresponding values.

    Returns:
        bool: True if the user data is valid, False otherwise.

    Raises:
        AssertionError: If any of the validation checks fail, an AssertionError is raised with a description of the failed check.
    """
    try:
        if 'id' in user: assert isinstance(user.get('id'), int) and user.get('id') > 0 # ids start with 1
        if 'name' in user: assert isinstance(user.get('name'), str) and len(user.get('name')) < 50 and len(user.get('name')) > 1
        if 'age' in user: assert isinstance(user.get('age'), int) and user.get('age') > 0 and user.get('age') < 150
        if 'city' in user: assert isinstance(user.get('city'), str) and len(user.get('city')) < 50 and len(user.get('city')) > 1
        if "date" in user: assert isinstance(user.get("date"), str) and re.match(r"^\d{4}-\d{2}-\d{2}$", user.get("date"))
        if "rating" in user: assert isinstance(user.get("rating"), int) and user.get("rating") < 11 and user.get("rating") >= 0
    except AssertionError:
        return False    
    return True

@app.route('/users', methods=['GET'])
def get_users() -> dict:
    """
    Retrieves a list of users from the CSV file, filtered by name or city.

    Returns:
        dict: A dictionary containing the list of filtered users, if name or city query parameters are provided,
            otherwise returns the complete list of users from the CSV file.
    """
    users = read_csv_file()
    name = request.args.get('name')
    city = request.args.get('city')

    if name or city: # if name or city return a user list filtered by name or city
        filtered_users = []
        for user in users: # allows for partial case insensitive matching
            if (name and name.lower() in user['name'].lower()) or (city and city.lower() in user['city'].lower()):
                filtered_users.append(user)                
        return {'users': filtered_users}, 200
    else:
        return {'users': users}, 200

@app.route('/users', methods=['POST'])
def add_user() -> dict:
    """
    Adds a user to the existing CSV table.

    Returns:
        dict: A dictionary containing the added user data if the user data is valid and successfully added to the table.
            Otherwise, returns an error dictionary with a 400 status code indicating invalid user data.
    """
    users = read_csv_file() 
    user = request.get_json()

    if not validate_user_data(user):
        return {'error': 'Invalid user data'}, 400
       
    user['id'] = generate_user_id(users)
    users.append(user)
    write_csv_file(users)

    return {'user': user}, 201

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int) -> dict:
    """
    Deletes a user from the existing CSV table by user ID.

    Args:
        user_id (int): The ID of the user to be deleted.

    Returns:
        dict: A dictionary containing the deleted user data if the user is found and successfully deleted from the table.
            Otherwise, returns an error dictionary with a 404 status code indicating user not found.
    """
    users = read_csv_file()    
        
    index = None
    for i, user in enumerate(users):
        if user['id'] == str(user_id): # grab user index by id match
            index = i
            break

    if index is not None: # if found - pop by index
        removed_user = users.pop(index)
        write_csv_file(users)
        return {'user': removed_user}, 200
    else:
        return {'error': 'User not found'}, 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def change_user(user_id: int) -> dict:
    """
    Changes user information in the existing CSV table by user ID.

    Args:
        user_id (int): The ID of the user to be updated.

    Returns:
        dict: A dictionary containing the updated user data if the user is found and successfully updated in the table.
            Otherwise, returns an error dictionary with a 404 status code indicating user not found.
    """
    users = read_csv_file()
    user = request.get_json()

    if not validate_user_data(user):
        return {'error': 'Invalid user data'}, 400
    
    
    updated_user = next((u for u in users if int(u['id']) == user_id), None)
    if updated_user:
        updated_user.update({key: value for key, value in user.items() if key in updated_user})
        write_csv_file(users)        
        return {'user': updated_user}, 201
    else:
        return {'error': 'User not found'}, 404
    
@app.route('/users/top', methods=['GET'])
def get_top_users() -> dict:
    """Returns the top n users by rating.

    Returns:
        dict: A JSON object containing information about the top n users, sorted by rating            
    """
    users = read_csv_file()
    n = int(request.args.get('n', 10))  # n value is passed inside a request, defaults to 10
    sorted_users = sorted(users, key=lambda x: x['rating'], reverse=True)  # sort by rating
    top_users = sorted_users[:n]  # get top n users

    return jsonify(top_users), 200

@app.route('/users/average_age', methods=['GET'])
def get_average_age_by_city() -> dict:
    """Returns the average user age by city.

    Returns:
        dict: A JSON object containing the average age of users for each city.            
    """
    age_by_city = {}  # temp dict for age sum and user count by city
    users = read_csv_file()
    for user in users:
        city = user['city']
        age = user['age']
        if user['age']:
            if city in age_by_city:
                age_by_city[city]['age_sum'] += int(age)
                age_by_city[city]['user_count'] += 1
            else:
                age_by_city[city] = {'age_sum': int(age), 'user_count': 1}
        average_age_by_city = {city: age_by_city[city]['age_sum'] / age_by_city[city]['user_count']
                            for city in age_by_city}
    
    return jsonify(average_age_by_city), 200

@app.route('/users/export', methods=['GET'])
def export_users_to_excel() -> dict:
    """Exports a table of users to an Excel file, filtered by city.

    Returns:
        dict: A JSON object containing a message indicating the success or failure of the export operation.            
    """
    users = read_csv_file()
    city = request.args.get('city')    
    city_users = [user for user in users if user['city'] == city]
    if len(city_users) > 0:
        df = pd.DataFrame(city_users)
        file_name = f'{city}_users.xlsx'
        df.to_excel(file_name, index=False)

        return {'message': f'Data on users from {city} was successfuly exported to: {file_name}'}, 200
    else:
        return {'message': f'No data on users from {city} is found'}, 404

if __name__ == '__main__':
    app.run(debug=True)
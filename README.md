# Users test task
___
### A basic implementation of a flask-API

This solution provides a flask API to interact with a simple .csv table.
The table contains mock user info for name, age, place of residence, and a unique ID for every added user.

### Provides the following functionality:
- Get list of existing users (can be filtered by name or place of residence) 
- Add a new user to the table
- Modify existing user's data

### Testing
___
In order to run tests, do:
```
cd users_test_task
python tests.py
```

### Launch locally:
___
```sh
# cloning repo
git clone git@github.com:DCCCXIX/users_test_task.git
cd users_test_task
```
```sh
# installing prerequisites
pip install -r requirements.txt
```
```sh
# launching flask server locally
# for linux/macos
export FLASK_APP=app.py
# for windows
set FLASK_APP=app.py
#
flask run
```
### Usage:
___
#### Get Users
Retrieves a list of users from the CSV file, filtered by name or city.
If the table is empty - will return a dict with an empty list as a value for 'users'
- URL: /users
- Method: GET
- Query Parameters:
-- name (optional): Filter users by name. Allows for partial, case-insensitive matching.
-- city (optional): Filter users by city. Allows for partial, case-insensitive matching.
- Response:
-- Status Code: 200 (OK)
- Body:
```
{
  "users": [
    {
      "id": "1",
      "name": "Anna Ivanova",
      "city": "Moscow"
    },
    {
      "id": "2",
      ...
    },
    ...
  ]
}
```

#### Add User
___
Adds a user to the existing CSV table.

- URL: /users
- Method: POST
- Request Body:
```
{
  "name": "Anna Ivanova",
  "age": 32,
  "city": "Moscow",
  "date": "1111-11-11",
  "rating": 10
}
```
- Response:
-- Status Code: 201 (Created)
- Body:
```
{
  "user": {
    "id": "1",
    "name": "Anna Ivanova",
    "age": 32,
    "city": "Moscow",
    "date": "1111-11-11",
    "rating": 10
  }
}
```
- Errors:
-- Status Code: 400 (Bad request)
```
{'error': 'Invalid user data'}
```

#### Delete User
___
Deletes a user from the existing CSV table by user ID.

- URL: /users/{user_id}
- Method: DELETE
- Path Parameters:
-- user_id: ID of the user to be deleted.
- Response:
-- Status Code: 200 (OK)
- Errors:
-- Status Code: 404 (Not Found)
```
{
  "error": "User not found"
}
```
#### Change User (PUT /users/<user_id>)
___
Changes user information in the existing CSV table by user ID.

- URL: /users/<user_id>
- Method: PUT
- Path Parameters:
-- user_id: (int) The ID of the user to be updated.
- Request Body:
```
{
  "user": {
    "id": "1",
    "name": "Anna Ivanova",
    "age": 32,
    "city": "Moscow",
    "date": "1111-11-11",
    "rating": 10
  }
}
```
- Response:
-- Status Code: 200 (OK)
-- Body:
```
{
  "user": {
    "id": "1",
    "name": "Anna Ivanova",
    "age": 32,
    "city": "Moscow",
    "date": "1111-11-11",
    "rating": 10
  }
}
```
- Errors:
-- Status Code: 404 (Not Found)
-- Status Code: 400 (Bad request)
```
{'error': 'Invalid user data'}
```
#### Get Top Users (GET /users/top)
___
Returns the top n users by rating.

- URL: /users/top
- Method: GET
- Query Parameters:
-- n: (optional) The number of top users to retrieve (default: 10)
- Response:
-- Status Code: 200 (OK)
-- Body:
```
{
  "users": [
    {
      "rating": "10",
      "name": "Anna Ivanova",
      "city": "Moscow"
    },
    {
      "rating": "9",
      ...
    },
    ...
  ]
}
```

#### Get Average Age by City (GET /users/average_age)
___
Returns the average user age by city.

- URL: /users/average_age
- Method: GET
- Query Parameters:
-- 'city' (required): The city for which users should be exported.
- Response:
-- Status Code: 200 (OK)
-- Body:
```
{
  "Moscow": 32.1,
  "Saint Petersburg": 29.8,
  ...
}
```

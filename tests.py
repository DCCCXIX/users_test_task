import unittest
from unittest.mock import mock_open, patch
import json
import os
from flask import Flask, request
from app import app, read_csv_file, write_csv_file

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):        
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()
                            # 'id', 'name', 'age', 'city', 'date', 'rating'
        self.mock_table = [
            {"id": 1, "name": "Oleg Babulekhov", "age": 80, "city": "Moscow", "date": "1943-12-01", "rating": 10},
            {"id": 2, "name": "Aristarch Kuralesov", "age": 22, "city": "Saint Petersburg", "date": "2001-11-02", "rating": 10},
            {"id": 3, "name": "Miroslav Popović", "age": 55, "city": "Belgrade", "date": "1968-10-03", "rating": 9},
            {"id": 4, "name": "Alexander Ivanov", "age": 35, "city": "Moscow", "date": "1988-09-04", "rating": 1},
            {"id": 5, "name": "Lexa Lexovich", "age": 14, "city": "Electrostal", "date": "2009-08-05", "rating": 3},
            {"id": 6, "name": "Epiphan Kozlov", "age": 40, "city": "Shatura", "date": "1983-07-06", "rating": 5},
            # id 7 is missing
            {"id": 8, "name": "Kirill Kurilov", "age": 32, "city": "Santa Barbara", "date": "1991-06-07", "rating": 5},                           
            {"id": 9, "name": "Oleg Olegov", "age": 70, "city": "Shatura", "date": "1953-05-08", "rating": 5},
            {"id": 10, "name": "Anna Annova", "age": 25, "city": "Moscow", "date": "1998-04-09", "rating": 2},
            {"id": 11, "name": "Veronica Ionotekova", "age": 22, "city": "Saint Petersburg", "date": "2001-03-10", "rating": 10},
            {"id": 12, "name": "Vadim Neludim", "age": 18, "city": "Electrostal", "date": "2005-02-11", "rating": 9},
            {"id": 13, "name": "Ekaterina Pokatukha", "age": 80, "city": "Moscow", "date": "1943-01-12", "rating": 7}
            ]

    def test_read_csv_file(self):
        table = read_csv_file()
        self.assertIsInstance(table, list)
        self.assertEqual(len(table), 12)
        self.assertEqual(table[0]["name"], "Oleg Babulekhov")
        self.assertEqual([user for user in table if user["name"]=="Kirill Kurilov"][0]["date"], "1991-06-07")

    def test_write_csv_file(self):
        write_csv_file(self.mock_table)
        self.assertTrue(os.path.isfile("users.csv"))   

    def test_get_users_with_no_query_params(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users' in response.get_json())
        self.assertEqual(len(response.get_json()['users']), 12)

    def test_get_users_with_name_query_param(self):
        response = self.client.get('/users?name=Oleg')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users' in response.get_json())
        self.assertEqual(len(response.get_json()["users"]), 2)

    def test_get_users_with_city_query_param(self):
        response = self.client.get('/users?city=Moscow')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users' in response.get_json())
        self.assertEqual(len(response.get_json()["users"]), 4)
        

    def test_add_user_with_valid_user_data(self):
        user = {"name": "Sanya Sutuly", "age": 88, "city": "Vorkuta", "date": "1943-12-01", "rating": 10}
        response = self.client.post('/users', json=user)
        self.assertEqual(response.status_code, 201)
        self.assertTrue('user' in response.get_json())

    def test_add_user_with_invalid_user_data(self):
        users = [{"id": 1, "name": 25, "age": 80, "city": "Moscow", "date": "1943-12-01", "rating": 10},
                 {"id": 1, "name": "Oleg Babulekhov", "age": 800, "city": "Moscow", "date": "1943-12-01", "rating": 10},
                 {"id": 1, "name": "Oleg Babulekhov", "age": 80, "city": "Moscow"*1000, "date": "1943-12-01", "rating": 10},
                 {"id": 1, "name": "Oleg Babulekhov", "age": 80, "city": "Moscow", "date": "1999", "rating": 10},
                 {"id": 1, "name": "Oleg Babulekhov"*1000, "age": 80, "city": "Moscow", "date": "1943-12-01", "rating": 10},
                 {"id": 1, "name": "Oleg Babulekhov", "age": 80, "city": "Moscow", "date": "1943-12-01", "rating": 100}                 
                 ]
        
        for user in users:
            response = self.client.post('/users', json=user)
            self.assertEqual(response.status_code, 400)
            self.assertTrue('error' in response.get_json())

    def test_delete_user_with_existing_user_id(self):
        user_id = 3
        response = self.client.delete(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('user' in response.get_json())

    def test_delete_user_with_nonexistent_user_id(self):
        user_id = 7
        response = self.client.delete(f'/users/{user_id}')
        self.assertEqual(response.status_code, 404)
        self.assertTrue('error' in response.get_json())

    def test_get_top_users(self):
        response = self.client.get('/users/top?n=5')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)  # Assert that the returned list has at most 5 users

    def test_get_average_age_by_city(self):
        response = self.client.get('/users/average_age')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(data, dict)
        self.assertTrue(all(isinstance(age, float) for age in data.values()))  # Assert that the values are floats

    def test_export_users_to_excel(self):
        response = self.client.get('/users/export?city=Saint Petersburg')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(data, dict)
        self.assertIn('message', data)
        self.assertIn('Saint Petersburg', data['message'])  # Assert that the city name is included in the message    

if __name__ == '__main__':
    unittest.main()
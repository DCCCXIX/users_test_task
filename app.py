from flask import Flask, request
from flask.json import jsonify
import csv

app = Flask(__name__)

def read_csv_file():
    """Helper function to read csv files"""
    pass

def write_csv_file():
    """Helper function to write csv files"""
    pass

def generate_user_id():
    """Helper function to generate user IDs"""
    pass

def validate_user_data():
    """User data validation"""
    pass

@app.route('/users', methods=['GET'])
def get_users():
    """Returns user list by name or city"""
    pass

@app.route('/users', methods=['POST'])
def add_user():
    """Adds a user to the existing table"""    
    pass

@app.route('/users/<int:user_id>', methods=['PUT'])
def change_user():
    """Change user info"""
    pass

if __name__ == '__main__':
    app.run(debug=True)
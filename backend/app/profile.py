import os
from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from psycopg2 import sql, Error
from app.db import get_db_connection, release_db_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a Blueprint for user profile management
profile = Blueprint('profile', __name__)

# Route to fetch user profile
@profile.route('/user_profile', methods=['GET'])
# @jwt_required()
def get_user_profile():
    user_id = 12
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CALL get_user_profile(%s, NULL, NULL, NULL, NULL);")
        result = cursor.fetchone()
        release_db_connection(conn)
        
        if result:
            return jsonify({
                "user_id": user_id,
                "height": result[0],
                "weight": result[1],
                "age": result[2],
                "goal": result[3]
            }), 200
        else:
            return jsonify({'message': 'User profile not found'}), 404
    
    except Error as e:
        current_app.logger.error(f'Error retrieving user profile: {e}')
        return jsonify({'error': 'An error occurred while fetching user profile'}), 500

# Route to add a new user profile
@profile.route('/user_profile', methods=['POST'])
# @jwt_required()
def add_user_profile():
    user_id = 12
    data = request.get_json()
    height = data.get('height')
    weight = data.get('weight')
    age = data.get('age')
    goal = data.get('goal')
    
    if not all([height, weight, age, goal]):
        return jsonify({'error': 'All fields (height, weight, age, goal) are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = sql.SQL("CALL insert_user_profile(%s, %s, %s, %s, %s);")
        cursor.execute(insert_query, (user_id, height, weight, age, goal))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'message': 'User profile added successfully'}), 201
    
    except Error as e:
        current_app.logger.error(f'Error adding user profile: {e}')
        return jsonify({'error': 'An error occurred while adding the user profile'}), 500

# Route to update an existing user profile
@profile.route('/user_profile', methods=['PUT'])
# @jwt_required()
def update_user_profile():
    user_id = 12
    data = request.get_json()
    height = data.get('height')
    weight = data.get('weight')
    age = data.get('age')
    goal = data.get('goal')
    
    if not all([height, weight, age, goal]):
        return jsonify({'error': 'All fields (height, weight, age, goal) are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = sql.SQL("CALL update_user_profile(%s, %s, %s, %s, %s);")
        cursor.execute(update_query, (user_id, height, weight, age, goal))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'message': 'User profile updated successfully'}), 200
    
    except Error as e:
        current_app.logger.error(f'Error updating user profile: {e}')
        return jsonify({'error': 'An error occurred while updating the user profile'}), 500

# Route to delete a user profile
@profile.route('/user_profile', methods=['DELETE'])
# @jwt_required()
def delete_user_profile():
    user_id = 12
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        delete_query = sql.SQL("CALL delete_user_profile(%s);")
        cursor.execute(delete_query, (user_id,))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'message': 'User profile deleted successfully'}), 200
    
    except Error as e:
        current_app.logger.error(f'Error deleting user profile: {e}')
        return jsonify({'error': 'An error occurred while deleting the user profile'}), 500

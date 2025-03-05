import os
from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from psycopg2 import sql, Error
import requests
from app.db import get_db_connection, release_db_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a Blueprint for food management
food = Blueprint('food', __name__)

# Route to fetch user’s food log
@food.route('/food_log', methods=['GET'])
# @jwt_required()
def get_food_log():
    user_id = 12
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CALL get_recent_calories(%s,'RESULT_CURSOR');", (user_id,))
        cursor.execute('FETCH ALL FROM "RESULT_CURSOR"')
        food_entries = cursor.fetchall()
        release_db_connection(conn)
        
        food_list = [
            {
                "food_id": entry[0],
                "food_name": entry[1],
                "calories": entry[2],
                "protein": entry[3],
                "carbs": entry[4],
                "fats": entry[5],
              
		 "date": entry[6]
            } for entry in food_entries
        ]
        
        return jsonify({"food_log": food_list}), 200
    
    except Error as e:
        current_app.logger.error(f'Error retrieving food log: {e}')
        return jsonify({'error': 'An error occurred while fetching food log'}), 500

# Route to add a new food entry
@food.route('/food_log', methods=['POST'])
# @jwt_required()
def add_food_entry():
    user_id = 12
    data = request.get_json()
    food_name = data.get('foodName')
    
    if not food_name:
        return jsonify({'error': 'foodName is required'}), 400
    
    try:
        # Fetch nutrition info from API Ninjas
        api_url = f"https://api.api-ninjas.com/v1/nutrition?query={food_name}"
        headers = {'X-Api-Key': os.getenv('APININJA_API_KEY')}
        response = requests.get(api_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch nutrition data'}), response.status_code
        
        api_data = response.json()
        if not api_data:
            return jsonify({'error': 'No nutrition data found for the given food'}), 404
        
        nutrition = api_data[0]
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein_g', 0)
        carbs = nutrition.get('carbohydrates_total_g', 0)
        fats = nutrition.get('fat_total_g', 0)
        
        # Insert food entry into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = sql.SQL("CALL insert_user_calories(%s, %s, %s, %s, %s, %s);")
        cursor.execute(insert_query, (user_id, food_name, calories, protein, carbs, fats))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({
            'message': 'Food entry added successfully',
            'food_name': food_name,
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats
        }), 201
    
    except Error as e:
        current_app.logger.error(f'Error adding food entry: {e}')
        return jsonify({'error': 'An error occurred while adding the food entry'}), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Route to delete a food entry
@food.route('/food_log/<int:food_id>', methods=['DELETE'])
# @jwt_required()
def delete_food_entry(food_id):
    user_id = 12
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        delete_query = sql.SQL("CALL delete_user_calories(%s);")
        cursor.execute(delete_query, (food_id,))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'message': 'Food entry deleted successfully', 'food_id': food_id}), 200
    
    except Error as e:
        current_app.logger.error(f'Error deleting food entry: {e}')
        return jsonify({'error': 'An error occurred while deleting the food entry'}), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Route to update an existing food entry
@food.route('/food_log/<int:food_id>', methods=['PUT'])
# @jwt_required()
def update_food_entry(food_id):
    user_id = 12
    data = request.get_json()
    food_name = data.get('foodName')
    
    if not food_name:
        return jsonify({'error': 'foodName is required'}), 400
    
    try:
        # Fetch updated nutrition info from API Ninjas
        api_url = f"https://api.api-ninjas.com/v1/nutrition?query={food_name}"
        headers = {'X-Api-Key': os.getenv('APININJA_API_KEY')}
        response = requests.get(api_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch updated nutrition data'}), response.status_code
        
        api_data = response.json()
        if not api_data:
            return jsonify({'error': 'No updated nutrition data found'}), 404
        
        nutrition = api_data[0]
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein_g', 0)
        carbs = nutrition.get('carbohydrates_total_g', 0)
        fats = nutrition.get('fat_total_g', 0)
        
        # Update food entry in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = sql.SQL("CALL update_user_calories(%s, %s, %s, %s, %s, %s);")
        cursor.execute(update_query, (food_id, food_name, calories, protein, carbs, fats))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'message': 'Food entry updated successfully', 'food_id': food_id}), 200
    
    except Error as e:
        current_app.logger.error(f'Error updating food entry: {e}')
        return jsonify({'error': 'An error occurred while updating the food entry'}), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500


######################### Calories #########################

# Route to fetch today's burned calories and workout duration
# Route to fetch today's burned calories and workout duration
@food.route('/today_calories_burnt', methods=['GET'])
# @jwt_required()
def get_today_calories_burnt():
    user_id = 12
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        get_query = sql.SQL("CALL get_today_calories_burnt(%s,null,null);")
        cursor.execute(get_query,(user_id,))
        result = cursor.fetchone()
        release_db_connection(conn)
        
        if result:
            return jsonify({"calories_burnt": result[0], "workout_duration": str(result[1])}), 200
        else:
            return jsonify({'message': 'No workout data found for today'}), 404
    
    except Error as e:
        current_app.logger.error(f'Error retrieving today’s calories burnt: {e}')
        return jsonify({'error': 'An error occurred while fetching data'}), 500


# Route to fetch today’s calories consumed
@food.route('/today_calories_consumed', methods=['GET'])
# @jwt_required()
def get_today_calories_consumed():
    user_id = 12
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        get_query = sql.SQL("CALL get_today_calories_consumed(%s,null);")
        cursor.execute(get_query,(user_id,))
        result = cursor.fetchone()
        release_db_connection(conn)
        
        if result and result[0] is not None:
            return jsonify({"calories_consumed": result[0]}), 200
        else:
            return jsonify({'message': 'No food data found for today'}), 404
    
    except Error as e:
        current_app.logger.error(f'Error retrieving today’s calories consumed: {e}')
        return jsonify({'error': 'An error occurred while fetching data'}), 500

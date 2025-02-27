import os
from flask import request, jsonify, Blueprint, current_app
from psycopg2 import sql, Error
from openai import OpenAI
# from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection, release_db_connection

# Create a Blueprint for the dashboard
dashboard = Blueprint('dashboard', __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))

# Route to fetch user’s height, weight, and goal, then send it to OpenAI
@dashboard.route('/user_fitness_analysis', methods=['GET'])
# @jwt_required()
def get_fitness_analysis():
    # user_id = get_jwt_identity()
    user_id = 1  # Placeholder, replace with the actual user authentication system
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch user fitness details
        query = sql.SQL("SELECT height, weight, goal FROM users WHERE user_id = %s;")
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        release_db_connection(conn)

        if not user_data:
            return jsonify({'error': 'User data not found'}), 404

        height, weight, goal = user_data

        # Send data to OpenAI API
        prompt = f"My height is {height} cm, my weight is {weight} kg, and my goal is {goal}. Suggest a personalized fitness plan."
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        ai_response = completion.choices[0].message.content  # Extract AI-generated content
        
        return jsonify({"ai_recommendation": ai_response}), 200
    
    except Error as e:
        current_app.logger.error(f'Error retrieving user data: {e}')
        return jsonify({'error': 'An error occurred while fetching user data'}), 500

# Route to get existing fitness activities
@dashboard.route('/activities', methods=['GET'])
# @jwt_required()
def get_activities():
    # user_id = get_jwt_identity()
    user_id = 1  # Placeholder
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = sql.SQL("SELECT activity_id, activity_name, duration, calories_burned FROM fitness_activities WHERE user_id = %s;")
        cursor.execute(query, (user_id,))
        activities = cursor.fetchall()
        release_db_connection(conn)
        
        activity_list = [
            {
                "activity_id": activity[0],
                "activity_name": activity[1],
                "duration": activity[2],
                "calories_burned": activity[3]
            } for activity in activities
        ]
        
        return jsonify({"activities": activity_list}), 200
    
    except Error as e:
        current_app.logger.error(f'Error retrieving activities: {e}')
        return jsonify({'error': 'An error occurred while fetching activities'}), 500

# Route to add a new fitness activity
@dashboard.route('/activities', methods=['POST'])
# @jwt_required()
def add_activity():
    # user_id = get_jwt_identity()
    user_id = 1  # Placeholder
    data = request.get_json()
    activity_name = data.get('activity_name')
    duration = data.get('duration')
    calories_burned = data.get('calories_burned')
    
    if not activity_name or not duration or not calories_burned:
        return jsonify({'error': 'All fields are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = sql.SQL("INSERT INTO fitness_activities (user_id, activity_name, duration, calories_burned) VALUES (%s, %s, %s, %s);")
        cursor.execute(insert_query, (user_id, activity_name, duration, calories_burned))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'message': 'Activity added successfully'}), 201
    
    except Error as e:
        current_app.logger.error(f'Error adding activity: {e}')
        return jsonify({'error': 'An error occurred while adding the activity'}), 500

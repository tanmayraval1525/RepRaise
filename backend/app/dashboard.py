import os
from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from psycopg2 import sql, Error
from openai import OpenAI
import requests
from app.db import get_db_connection, release_db_connection
from dotenv import load_dotenv

# Create a Blueprint for the dashboard
dashboard = Blueprint('dashboard', __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))
load_dotenv()

# Route to fetch user’s height, weight, and goal, then send it to OpenAI
@dashboard.route('/user_fitness_analysis', methods=['GET'])
@jwt_required()
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

        height, weight,age, goal = user_data

        # Send data to OpenAI API
        prompt = f"My height is {height} cm, my weight is {weight} kg,my age is {age} and my goal is {goal}. Suggest a personalized fitness plan."
        
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
    user_id = 12
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # get_activities = sql.SQL("CALL get_recent_activities(%s, \"result_cursor\");")
        # cursor.execute(get_activities, (user_id,))
        cursor.execute("CALL get_recent_activities(%s, 'result_cursor');", (user_id,))
        cursor.execute("fetch all in \"result_cursor\"")
        activities = cursor.fetchall()
        release_db_connection(conn)
        
        activity_list = [
            {
                "activity_id": activity[0],
                "activity_name": activity[1],
                "duration": activity[2],
                "calories_burned": activity[3],
                "Date": activity[4]
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
    user_id = 12
    data = request.get_json()
    activity_name = data.get('activityName')
    duration = int(data.get('activityDuration'))
    
    # Validate required fields
    if not activity_name or not duration:
        return jsonify({'error': 'activity_name and duration are required'}), 400
    
    try:
        # Fetch calories burned from the third-party API
        api_url = f"https://api.api-ninjas.com/v1/caloriesburned?activity={activity_name}"
        headers = {'X-Api-Key': os.getenv('APININJA_API_KEY')}
        response = requests.get(api_url, headers=headers)
        
        # Check if the API request was successful
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch calories burned from the API'}), response.status_code
        
        # Parse the API response
        api_data = response.json()
        if not api_data:
            return jsonify({'error': 'No data found for the given activity'}), 404
        
        # Extract calories burned per hour (assuming the first result is the most relevant)
        calories_per_hour = int(api_data[0].get('calories_per_hour'))
        if not calories_per_hour:
            return jsonify({'error': 'Calories data not found in API response'}), 404
        
        # Calculate total calories burned based on duration
        calories_burned = (calories_per_hour * duration) / 60  # Convert duration to hours
        
        # Insert the activity into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = sql.SQL("CALL insert_user_activity(%s, %s, %s, %s);")
        cursor.execute(insert_query, (user_id, activity_name, duration, calories_burned))
        conn.commit()
        release_db_connection(conn)
        
        # Return success response
        return jsonify({
            'message': 'Activity added successfully',
            'activity_name': activity_name,
            'duration': duration,
            'calories_burned': calories_burned
        }), 201
    
    except Error as e:
        current_app.logger.error(f'Error adding activity: {e}')
        return jsonify({'error': 'An error occurred while adding the activity'}), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
    # Delete an activity
@dashboard.route('/activities/<int:activity_id>', methods=['DELETE'])
# @jwt_required()
def delete_activity(activity_id):
    user_id = 12
    
    try:
        # Delete the activity from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        delete_query = sql.SQL("CALL delete_user_activity(%s, %s);")
        cursor.execute(delete_query, (activity_id, user_id))
        conn.commit()
        release_db_connection(conn)
        
        # Return success response
        return jsonify({
            'message': 'Activity deleted successfully',
            'activity_id': activity_id
        }), 200
    
    except Error as e:
        current_app.logger.error(f'Error deleting activity: {e}')
        return jsonify({'error': 'An error occurred while deleting the activity'}), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Update an existing activity
@dashboard.route('/activities/<int:activity_id>', methods=['PUT'])
# @jwt_required()
def update_activity(activity_id):
    user_id = 12
    data = request.get_json()
    activity_name = data.get('activityName')
    duration = data.get('activityDuration')
    
    # Validate required fields
    if not activity_name or not duration:
        return jsonify({'error': 'activity_name and duration are required'}), 400
    
    try:
        # Fetch calories burned from the third-party API
        api_url = f"https://api.api-ninjas.com/v1/caloriesburned?activity={activity_name}"
        headers = {'X-Api-Key': os.getenv('APININJA_API_KEY')}
        response = requests.get(api_url, headers=headers)
        
        # Check if the API request was successful
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch calories burned from the API'}), response.status_code
        
        # Parse the API response
        api_data = response.json()
        if not api_data:
            return jsonify({'error': 'No data found for the given activity'}), 404
        
        # Extract calories burned per hour (assuming the first result is the most relevant)
        calories_per_hour = int(api_data[0].get('calories_per_hour'))
        if not calories_per_hour:
            return jsonify({'error': 'Calories data not found in API response'}), 404
        
        # Calculate total calories burned based on duration
        calories_burned = (calories_per_hour * duration) / 60  # Convert duration to hours
        # duration = str(duration)
        
        # Update the activity in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = sql.SQL("CALL update_user_activity(%s, %s, %s, %s, %s);")
        cursor.execute(update_query, (activity_id, user_id, activity_name, duration, calories_burned))
        conn.commit()
        release_db_connection(conn)
        
        # Return success response
        return jsonify({
            'message': 'Activity updated successfully',
            'activity_id': activity_id,
            'activity_name': activity_name,
            'duration': duration,
            'calories_burned': calories_burned
        }), 200
    
    except Error as e:
        current_app.logger.error(f'Error updating activity: {e}')
        return jsonify({'error': 'An error occurred while updating the activity'}), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

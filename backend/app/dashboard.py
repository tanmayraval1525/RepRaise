from flask import request, jsonify, Blueprint, current_app
from psycopg2 import sql, Error
from openai import OpenAI

# from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection, release_db_connection

# Create a Blueprint for the dashboard


dashboard = Blueprint('dashboard', __name__)

client = OpenAI(
    open_api_key=os.getenv('OPEN_API_KEY'),
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);

# Route to get existing fitness activities
@dashboard.route('/activities', methods=['GET'])
# @jwt_required()
def get_activities():
    # user_id = get_jwt_identity()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = sql.SQL("SELECT activity_id, activity_name, duration, calories_burned FROM fitness_activities WHERE user_id = %s;")
        cursor.execute(query, (user_id,))
        activities = cursor.fetchall()
        release_db_connection(conn)
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                "activity_id": activity[0],
                "activity_name": activity[1],
                "duration": activity[2],
                "calories_burned": activity[3]
            })
        
        return jsonify({"activities": activity_list}), 200
    
    except Error as e:
        current_app.logger.error(f'Error retrieving activities: {e}')
        return jsonify({'error': 'An error occurred while fetching activities'}), 500


# Route to add a new fitness activity
@dashboard.route('/activities', methods=['POST'])
# @jwt_required()
def add_activity():
    # user_id = get_jwt_identity()
    data = request.get_json()
    activity_name = data.get('activity_name')
    duration = data.get('duration')
    calories_burned = data.get('calories_burned')
    
    if not activity_name or not duration or not calories_burned:
        return jsonify({'error': 'All fields are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = sql.SQL("INSERT INTO fitness_activities (activity_name, duration, calories_burned) VALUES (%s, %s, %s);")
        cursor.execute(insert_query, (activity_name, duration, calories_burned))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'message': 'Activity added successfully'}), 201
    
    except Error as e:
        current_app.logger.error(f'Error adding activity: {e}')
        return jsonify({'error': 'An error occurred while adding the activity'}), 500

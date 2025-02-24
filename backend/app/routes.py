from flask import Flask, request, jsonify, Blueprint,current_app
from psycopg2 import sql,Error
from flask_jwt_extended import  create_access_token, jwt_required, get_jwt_identity
from app.db import get_db_connection,release_db_connection
#from sqlalchemy.exc import SQLAlchemyError
from app import bcrypt,jwt


main = Blueprint('main', __name__)

user_id = 0

@main.route('/')
def home():
    return jsonify({"message": "Welcome to the Fitness App API!"})

# Signup Route
@main.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    fname = data.get('firstName')
    lname = data.get('lastName')

    if not fname or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = sql.SQL("CALL user_signup(%s, %s, %s, %s, NULL);")
        cursor.execute(insert_query, (fname, lname, email, hashed_password))
        user_id = cursor.fetchone()[0]
        conn.commit()
        release_db_connection(conn)
        if not user_id:
            return jsonify({'error': 'User already exists'}), 400
        else:
            return jsonify({'message': 'User created successfully '}), 201
        
    except Error as e:
        current_app.logger.error(f'Error creating user: {e}')
        return jsonify({'error': 'An error occurred while creating the user'}), 500
    
# Login Route
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    login_query = sql.SQL("CALL getLoginDetails(%s, NULL, NULL);")
    cursor.execute(login_query, (email,))
    result = cursor.fetchone()
    password_db_val = result[0]
    user_id_db_val = result[1]
    conn.commit()
    release_db_connection(conn)

    if not email or not password:
        return jsonify({'error': 'Invalid email or password'}), 400
    if password_db_val and bcrypt.check_password_hash(password_db_val, password):
        access_token = create_access_token(identity=user_id_db_val)
        return jsonify({'message': 'Login successful', 'token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

# Protected Route Example
# @main.route('/profile', methods=['GET'])
# @jwt_required()
# def profile():
#     user_id = get_jwt_identity()
#     user = User.query.get(user_id)

#     if user:
#         return jsonify({'username': user.username, 'email': user.email})
#     return jsonify({'error': 'User not found'}), 404


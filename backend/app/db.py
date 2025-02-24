import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Create a connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 80,  # Min and max connections
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME')
    )
    
    if connection_pool:
        print("Database connection pool created successfully!")

except Exception as e:
    print(f"Error connecting to the database: {e}")


# Function to get a connection from the pool
def get_db_connection():
    try:
        conn = connection_pool.getconn()
        if conn:
            print("Successfully retrieved a connection from the pool.")
        return conn
    except Exception as e:
        print(f"Error getting connection: {e}")
        return None


# Function to return the connection back to the pool
def release_db_connection(conn):
    try:
        if conn:
            connection_pool.putconn(conn)
            print("Connection returned to the pool.")
    except Exception as e:
        print(f"Error releasing connection: {e}")

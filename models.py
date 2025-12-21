# models.py
"""
Database access layer for The Voyager application.
Handles all CRUD operations for users, trips, and itinerary days.
Uses PyMySQL with parameterized queries for security.
"""

import pymysql
from pymysql.cursors import DictCursor
from pymysql.err import IntegrityError
from config import Config


# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def get_db():
    """
    Create and return a new database connection.
    Returns a connection with DictCursor to get results as dictionaries.
    """
    conn = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    return conn


# ============================================================================
# USER OPERATIONS
# ============================================================================

def create_user(username, password_hash):
    """
    Create a new user in the database.
    
    Args:
        username: Unique username for the account
        password_hash: Hashed password (already encrypted)
    
    Returns:
        int: The ID of the newly created user
    
    Raises:
        IntegrityError: If username already exists
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
            cursor.execute(query, (username, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
    except IntegrityError as e:
        # Username already exists (UNIQUE constraint violation)
        conn.rollback()
        raise e
    finally:
        conn.close()


def find_user(username):
    """
    Find a user by username.
    
    Args:
        username: The username to search for
    
    Returns:
        dict: User record with keys 'id', 'username', 'password_hash'
        None: If user not found
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = "SELECT id, username, password_hash FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            return user
    finally:
        conn.close()


# ============================================================================
# TRIP OPERATIONS
# ============================================================================

def create_trip(user_id, title, num_days, prefs):
    """
    Create a new trip itinerary.
    
    Args:
        user_id: ID of the user creating the trip
        title: Trip title/destination name
        num_days: Number of days in the itinerary
        prefs: User preferences for the trip (optional)
    
    Returns:
        int: The ID of the newly created trip
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO trips (user_id, title, num_days, preferences)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, title, num_days, prefs))
            conn.commit()
            trip_id = cursor.lastrowid
            return trip_id
    finally:
        conn.close()


def get_trip(trip_id):
    """
    Retrieve a single trip by ID.
    
    Args:
        trip_id: The trip's ID
    
    Returns:
        dict: Trip record with all fields
        None: If trip not found
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM trips WHERE id = %s"
            cursor.execute(query, (trip_id,))
            trip = cursor.fetchone()
            return trip
    finally:
        conn.close()


def get_trips_by_user(user_id):
    """
    Retrieve all trips for a specific user.
    
    Args:
        user_id: The user's ID
    
    Returns:
        list[dict]: List of trip records (newest first)
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM trips WHERE user_id = %s ORDER BY id DESC"
            cursor.execute(query, (user_id,))
            trips = cursor.fetchall()
            return trips
    finally:
        conn.close()


def delete_trip(trip_id):
    """
    Delete a trip by ID.
    This will cascade delete all associated itinerary days.
    
    Args:
        trip_id: The trip's ID
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = "DELETE FROM trips WHERE id = %s"
            cursor.execute(query, (trip_id,))
            conn.commit()
    finally:
        conn.close()


# ============================================================================
# ITINERARY DAY OPERATIONS
# ============================================================================

def create_day(trip_id, day_number, content):
    """
    Create a new itinerary day entry.
    
    Args:
        trip_id: The trip this day belongs to
        day_number: The day number (1-indexed)
        content: The itinerary content/summary for this day
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO itinerary_days (trip_id, day_number, content)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (trip_id, day_number, content))
            conn.commit()
    finally:
        conn.close()


def get_days(trip_id):
    """
    Retrieve all itinerary days for a trip, ordered by day number.
    
    Args:
        trip_id: The trip's ID
    
    Returns:
        list[dict]: List of day records with 'day_number' and 'content'
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT day_number, content
                FROM itinerary_days
                WHERE trip_id = %s
                ORDER BY day_number
            """
            cursor.execute(query, (trip_id,))
            days = cursor.fetchall()
            return days
    finally:
        conn.close()


def update_day(trip_id, day_number, new_content):
    """
    Update the content of a specific day in an itinerary.
    
    Args:
        trip_id: The trip's ID
        day_number: The day number to update
        new_content: The new itinerary content for this day
    """
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            query = """
                UPDATE itinerary_days
                SET content = %s
                WHERE trip_id = %s AND day_number = %s
            """
            cursor.execute(query, (new_content, trip_id, day_number))
            conn.commit()
    finally:
        conn.close()


# ============================================================================
# UTILITY FUNCTIONS (OPTIONAL)
# ============================================================================

def init_db(schema_file='schema.sql'):
    """
    Initialize the database by executing the schema SQL file.
    This is optional and used for development/testing setup.
    
    Args:
        schema_file: Path to the SQL schema file
    """
    conn = get_db()
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Split by semicolons to execute multiple statements
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        with conn.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
            conn.commit()
        
        print("Database initialized successfully")
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise e
    finally:
        conn.close()
# app.py
"""
Main Flask application for The Voyager.
Handles user authentication, trip creation, and itinerary management.
"""

from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash

# Import our custom modules
from config import Config
import models
import openai_service


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CSRF protection globally
csrf = CSRFProtect(app)


# ============================================================================
# FORM DEFINITIONS
# ============================================================================

class RegistrationForm(FlaskForm):
    """Form for new user registration."""
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=50, message='Username must be between 3 and 50 characters')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, message='Password must be at least 6 characters')
        ]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField(
        'Username',
        validators=[DataRequired(message='Username is required')]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required')]
    )
    submit = SubmitField('Login')


class NewTripForm(FlaskForm):
    """Form for creating a new trip itinerary."""
    title = StringField(
        'Destination',
        validators=[
            DataRequired(message='Destination is required'),
            Length(max=100, message='Destination must be less than 100 characters')
        ]
    )
    num_days = IntegerField(
        'Number of Days',
        validators=[
            DataRequired(message='Number of days is required'),
            NumberRange(min=1, max=30, message='Trip must be between 1 and 30 days')
        ]
    )
    preferences = TextAreaField(
        'Preferences',
        description='Optional: dietary restrictions, interests, budget, etc.'
    )
    submit = SubmitField('Generate Itinerary')


# ============================================================================
# LOGIN REQUIRED DECORATOR
# ============================================================================

def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration page.
    GET: Display registration form
    POST: Create new user account
    """
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check if username already exists
        existing_user = models.find_user(username)
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('register.html', form=form)
        
        # Hash the password for secure storage
        password_hash = generate_password_hash(password)
        
        # Create the user in the database
        try:
            user_id = models.create_user(username, password_hash)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'error')
            print(f"Registration error: {e}")
            return render_template('register.html', form=form)
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page.
    GET: Display login form
    POST: Authenticate user and create session
    """
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Find user by username
        user = models.find_user(username)
        
        # Verify user exists and password is correct
        if user and check_password_hash(user['password_hash'], password):
            # Set session data to log the user in
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return render_template('login.html', form=form)
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """
    Log out the current user by clearing the session.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# TRIP MANAGEMENT ROUTES
# ============================================================================

@app.route('/')
@login_required
def dashboard():
    """
    Main dashboard showing all trips for the logged-in user.
    """
    user_id = session['user_id']
    
    # Fetch all trips belonging to this user
    trips = models.get_trips_by_user(user_id)
    
    return render_template('dashboard.html', trips=trips)


@app.route('/trip/new', methods=['GET', 'POST'])
@login_required
def new_trip():
    """
    Create a new trip with AI-generated itinerary.
    GET: Display trip creation form
    POST: Generate itinerary and save to database
    """
    form = NewTripForm()
    
    if form.validate_on_submit():
        user_id = session['user_id']
        title = form.title.data
        num_days = form.num_days.data
        preferences = form.preferences.data or ''
        
        try:
            # Call OpenAI to generate the itinerary
            itinerary_data = openai_service.generate_itinerary(
                destination=title,
                days=num_days,
                prefs=preferences
            )
            
            # Validate that we received itinerary data
            if not itinerary_data or 'days' not in itinerary_data:
                flash('Failed to generate itinerary. Please try again.', 'error')
                return render_template('new_trip.html', form=form)
            
            # Create the trip record in the database
            trip_id = models.create_trip(user_id, title, num_days, preferences)
            
            # Save each day's itinerary to the database
            for day_data in itinerary_data['days']:
                day_number = day_data['day']
                content = day_data['summary']
                models.create_day(trip_id, day_number, content)
            
            flash('Trip itinerary created successfully!', 'success')
            return redirect(url_for('trip_view', trip_id=trip_id))
            
        except Exception as e:
            flash('An error occurred while generating the itinerary. Please try again.', 'error')
            print(f"Trip creation error: {e}")
            import traceback
            traceback.print_exc()
            return render_template('new_trip.html', form=form)
    
    return render_template('new_trip.html', form=form)


@app.route('/trip/<int:trip_id>')
@login_required
def trip_view(trip_id):
    """
    View the itinerary for a specific trip.
    Ensures the trip belongs to the logged-in user.
    """
    user_id = session['user_id']
    
    # Fetch the trip details
    trip = models.get_trip(trip_id)
    
    # Verify trip exists and belongs to current user
    if not trip:
        flash('Trip not found.', 'error')
        return redirect(url_for('dashboard'))
    
    if trip['user_id'] != user_id:
        flash('You do not have permission to view this trip.', 'error')
        return redirect(url_for('dashboard'))
    
    # Fetch all days for this trip
    days = models.get_days(trip_id)
    
    return render_template('itinerary.html', trip=trip, days=days)


@app.route('/trip/<int:trip_id>/day/<int:day_num>/regenerate', methods=['POST'])
@login_required
def regenerate_day(trip_id, day_num):
    """
    AJAX endpoint to regenerate a single day's itinerary.
    Returns JSON response with updated content.
    """
    user_id = session['user_id']
    
    # Fetch the trip and verify ownership
    trip = models.get_trip(trip_id)
    
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    
    if trip['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate day number
    if day_num < 1 or day_num > trip['num_days']:
        return jsonify({'error': 'Invalid day number'}), 400
    
    try:
        # Call OpenAI to regenerate just this day
        day_data = openai_service.regenerate_day(
            destination=trip['title'],
            day_num=day_num,
            total_days=trip['num_days'],
            prefs=trip['preferences'] or ''
        )
        
        # Validate response
        if not day_data or 'summary' not in day_data:
            return jsonify({'error': 'Failed to generate new itinerary'}), 500
        
        # Verify the day number matches
        if day_data.get('day') != day_num:
            return jsonify({'error': 'Day number mismatch'}), 500
        
        # Update the database with new content
        new_content = day_data['summary']
        models.update_day(trip_id, day_num, new_content)
        
        # Return success response with new content
        return jsonify({
            'day': day_num,
            'content': new_content
        })
        
    except Exception as e:
        print(f"Regenerate day error: {e}")
        return jsonify({'error': 'An error occurred while regenerating the day'}), 500


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Run the Flask development server
    # Debug mode enabled for local development
    app.run(debug=True, host='127.0.0.1', port=5000)
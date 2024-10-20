from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from bson import ObjectId
import os
import secrets
import serial
import time
import subprocess  # Required for subprocess call

app = Flask(__name__)

# Serial port settings
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600

# Attempt to establish a serial connection
def establish_serial_connection():
    try:
        serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        if serial_connection.is_open:
            return serial_connection, None
        else:
            return None, f"Failed to open port {SERIAL_PORT}. Please check the connection."
    except serial.SerialException as e:
        return None, f"Error: {str(e)}"

serial_connection, connection_error = establish_serial_connection()

@app.route('/connect-tank', methods=['POST'])
def connect_tank():
    global serial_connection, connection_error

    if serial_connection is None:
        # Attempt to re-establish the connection if it was lost
        serial_connection, connection_error = establish_serial_connection()

    if serial_connection is None:
        return jsonify({'success': False, 'message': connection_error})
    
    return jsonify({'success': True, 'message': 'Tank is connected successfully!'})

# Route to start Pygame after connection
@app.route('/start-tank')
def start_tank():
    try:
        # Run the Pygame script to show the tank on screen
        subprocess.Popen(['python', 'tank_visualization.py'])  # Run Pygame script
        return redirect(url_for('index'))  # Redirect to home page
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

app.config["MONGO_URI"] = "mongodb://localhost:27017/h20manager"  # Database name: h20manager
app.config['SECRET_KEY'] = os.urandom(24)  # Generates a random 24-byte key

mongo = PyMongo(app)

# Route for the landing page (index)
@app.route('/')
def index():
    return render_template('index.html')

def serialize_object(obj):
    """Helper function to serialize MongoDB's ObjectId to string."""
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

# Function to load the dataset and preprocess it
def load_and_preprocess_data():
    df = pd.read_csv('DATASET - Sheet1.csv')
    df['WATER REQUIREMENT'] = pd.to_numeric(df['WATER REQUIREMENT'], errors='coerce')
    df.dropna(subset=['WATER REQUIREMENT'], inplace=True)

    categorical_columns = ['CROP TYPE', 'SOIL TYPE', 'REGION', 'TEMPERATURE', 'WEATHER CONDITION']
    df_encoded = pd.get_dummies(df, columns=categorical_columns)

    X = df_encoded.drop('WATER REQUIREMENT', axis=1)
    y = df_encoded['WATER REQUIREMENT']

    return X, y, df_encoded

# Function to train and save the model
def train_model():
    X, y, _ = load_and_preprocess_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    joblib.dump(model, 'water_model.pkl')

# Function to load the trained model
def load_model():
    return joblib.load('water_model.pkl')

# Route for the forecast page with water requirement prediction
@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    if request.method == 'POST':
        crop = request.form['crop']
        soil = request.form['soil']
        region = request.form['region']
        temperature = request.form['temperature']
        weather = request.form['weather']

        _, _, df_encoded = load_and_preprocess_data()

        input_data = {
            'CROP TYPE_' + crop: 1,
            'SOIL TYPE_' + soil: 1,
            'REGION_' + region: 1,
            'TEMPERATURE_' + temperature: 1,
            'WEATHER CONDITION_' + weather: 1
        }

        input_df = pd.DataFrame(0, index=[0], columns=df_encoded.columns.drop('WATER REQUIREMENT'))
        input_df.update(pd.DataFrame(input_data, index=[0]))

        model = load_model()
        prediction = model.predict(input_df)[0]

        return render_template('forecast.html', prediction=prediction)

    return render_template('forecast.html')

# Route for the reservoirs page
@app.route('/reservoirs')
def reservoirs():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('tank1.html')  # Direct to tank1.html as per logic

@app.route('/tank1')
def tank1():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('tank1.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract user data from form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            return "User already exists!"

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert user data into MongoDB
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })

        return redirect(url_for('login'))  # Redirect to login page after successful signup

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find the user by email
        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            # Create session for the logged-in user
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))  # Redirect to the home page after successful login
        else:
            # If credentials are invalid, pass an error message
            error = "Invalid email or password. Please try again."
            return render_template('login.html', error=error)
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the session
    return redirect(url_for('index'))  

@app.route('/chatbot')
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('chatbot.html')

# Route for the footprint page
@app.route('/footprint')
def footprint():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('footprint.html')

if __name__ == '__main__':
    app.run(debug=True)

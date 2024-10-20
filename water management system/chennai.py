from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd

app.secret_key = '7d17f0b36a5322f17bff70c355e7bb2ad8095d2723119579c65539fdf2365ddb'  
from aixplain.factories.models import ModelFactory

app = Flask(__name__)
app.secret_key = '7d17f0b36a5322f17bff70c355e7bb2ad8095d2723119579c65539fdf2365ddb'  # Replace with your actual secret key

# Load aiXplain model
def load_aixplain_model():
    model_id = '6622cf096eb563537126b1a1'  # Your aiXplain model ID
    model = ModelFactory.get(model_id)
    return model

@app.route('/chennai', methods=['GET', 'POST'])
def chennai():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    if request.method == 'POST':
        # Get form input values
        region = request.form['region']
        month = request.form['month']

        # Prepare the input for the aiXplain model
        input_data = {
            "region": region,
            "month": month
        }

        # Load and use aiXplain model for prediction
        model = load_aixplain_model()
        prediction = model.predict(input_data)

        # Extract predicted water requirement from the model output
        water_requirement = prediction['result']['total']  # Adjust based on model's output format

        return render_template('chennai.html', water_requirement=water_requirement)

    return render_template('chennai.html')

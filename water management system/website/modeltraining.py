import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# Function to load and preprocess the data
def load_and_preprocess_data():
    df = pd.read_csv('DATASET - Sheet1.csv')  # Make sure the dataset is in the right path
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

    # Save the trained model
    joblib.dump(model, 'water_model.pkl')
    print("Model trained and saved as water_model.pkl")

# Call the train_model function to regenerate the model
train_model()

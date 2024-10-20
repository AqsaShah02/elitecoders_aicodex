import os
os.environ['TEAM_API_KEY'] = '64c4a9fb8d26148cdf7ca52fbd515108caa5bbe3ff9827babdb150801c561a3f'

from aixplain.factories import ModelFactory

# Initialize the aiXplain model
model = ModelFactory.get("6414bd3cd09663e9225130e8")  # Replace with your actual model ID

# Prepare a sample input
input_text = (
    f"Water usage analysis:\n"
    f"Average monthly water usage: 145 liters.\n"
    f"Maximum water usage: 200 liters in July.\n"
    f"Minimum water usage: 100 liters in February.\n"
    f"Generate a detailed analysis and suggest water conservation methods."
)

try:
    print("Sending input to AI model:", input_text)
    result = model.run({
        'text': input_text
    })
    print("Model result:", result)
except Exception as e:
    print(f"Error while calling the model: {e}")

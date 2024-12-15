from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define your routes as before
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'cleaneddata.csv')
        data = pd.read_csv(file_path)
        return data.to_json(orient='records')  # Returns the dataset as a JSON response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_data():
    try:
        input_data = request.json  # Example input from the frontend
        result = {'message': 'Data processed successfully!', 'input': input_data}
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

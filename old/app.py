from flask import Flask, render_template, request, jsonify
import numpy as np # Just in case you're doing math

app = Flask(__name__)

@app.route('/')
def index():
    # This serves your HTML file
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    user_input = data.get('value')

    # --- SIMULATE ML MODEL LOGIC ---
    # Replace this with: model.predict([[user_input]])
    try:
        score = len(user_input) * 10 # Example "ML" logic
        status = "High" if score > 50 else "Low"
        
        return jsonify({
            "status": "success",
            "prediction": score,
            "category": status
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
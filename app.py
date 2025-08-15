from flask import Flask, render_template, request, send_file, session, url_for, redirect
import subprocess
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_IMAGE = 'output_image.png'
app.secret_key = 'your_secret_key'  # Needed for session

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createJSON')
def create_json():
    return render_template('createJSON.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get uploaded JSON file and argument
    file = request.files.get('json_file')
    money = request.form.get('money')
    days = request.form.get('days')

    if not file or file.filename == '':
        return 'No JSON file uploaded.'

    if not money:
        return 'No current money provided.'
    
    if not days:
        days = '50'  # Default to 50 days if not provided

    # Save uploaded JSON file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Call the external Python script
    try:
        result = subprocess.run(
            ['python', 'run.py',  '-f', filepath, '-m', money, '-d', days],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"Script error:<br><pre>{result.stderr}</pre>"

    except Exception as e:
        return f"Error running script: {str(e)}"

    # Check if image exists
    image_path = "images/" + OUTPUT_IMAGE
    if not os.path.exists("images/" + OUTPUT_IMAGE):
        return "Image was not generated."
    
    session['image_path'] = image_path
    return redirect(url_for('result'))

    # # Return the image to the browser
    # return send_file("images/" + OUTPUT_IMAGE, mimetype='image/png')

@app.route('/result')
def result():
    image_path = session.get('image_path')
    if not image_path or not os.path.exists(image_path):
        return "No image to display."
    transactions_text = []
    try:
        with open('media/transactions.txt', 'r') as f:
            for line in f:
                transactions_text.append(line)
    except Exception as e:
        transactions_text = f"Error loading transactions: {e}"
    # Pass the image route to the template
    return render_template('result.html', image_url=url_for('display_image'), transactions_text=transactions_text)

@app.route('/display_image')
def display_image():
    image_path = session.get('image_path')
    if not image_path or not os.path.exists(image_path):
        return "No image found.", 404
    return send_file(image_path, mimetype='image/png')

# app.run(host='0.0.0.0')
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:5001')

@app.route('/')
def index():
    # Get submissions from backend
    try:
        response = requests.get(f"{BACKEND_URL}/api/submissions")
        if response.status_code == 200:
            submissions = response.json()
        else:
            submissions = []
            flash("Failed to load submissions")
    except requests.exceptions.RequestException:
        submissions = []
        flash("Backend service unavailable")
        
    return render_template('index.html', submissions=submissions)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content:
            flash("Content is required!")
            return render_template('submit.html')
            
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/submit", 
                json={"content": content}
            )
            
            if response.status_code == 201:
                flash("Form submitted successfully!")
                return redirect(url_for('index'))
            else:
                flash(f"Error: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException:
            flash("Backend service unavailable")
            
    return render_template('submit.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
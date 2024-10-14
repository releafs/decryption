import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

# Configuration for the upload folder
UPLOAD_FOLDER = 'input/'
ALLOWED_EXTENSIONS = {'png'}

# Create the 'input' folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the uploaded file is allowed (only PNG files)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the upload page
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Route to handle file upload
@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('file')
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_files.append(filename)
    
    if uploaded_files:
        return f"Files uploaded successfully: {', '.join(uploaded_files)}"
    else:
        return "No valid PNG files were uploaded."

# Main function to run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

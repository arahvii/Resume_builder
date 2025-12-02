from flask import Flask, render_template, request, send_file
# FIX 1: Use relative import to resolve ModuleNotFoundError and the yellow highlight issue
from .reportlab_generator import generate_resume_pdf
from io import BytesIO

app = Flask(__name__)

# Route for the main page (GET request)
@app.route('/', methods=['GET'])
def index():
    """Renders the main resume input form."""
    return render_template('index.html')

# FIX 3: Dedicated route for handling the form submission (POST request)
@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    """Collects form data and generates the PDF resume."""
    
    # Start with all simple text fields
    data = request.form.to_dict()

    # --- Collect List Fields (Experience, Skills, Languages, Interests) ---

    # Experience details (all are lists of the same length)
    data['exp_titles'] = request.form.getlist('exp_titles[]')
    data['exp_companies'] = request.form.getlist('exp_companies[]')
    data['exp_dates'] = request.form.getlist('exp_dates[]')
    data['exp_locations'] = request.form.getlist('exp_locations[]')

    # FIX 2: Correctly collect the raw JSON string data for Key Achievements.
    # The reportlab_generator.py function will handle the JSON parsing.
    data['exp_bullets_json'] = request.form.getlist('exp_bullets_json[]')

    # --- Image Handling ---
    image_data = None
    if 'profile_image' in request.files:
        image_file = request.files['profile_image']
        
        # Check if a file was actually uploaded and it has content
        if image_file and image_file.filename:
            # Read the file's binary content
            image_data = image_file.read()

    # --- PDF Generation ---
    try:
        buffer = generate_resume_pdf(data, image_data)
        
        # Determine the filename for the download
        name_for_file = data.get('name', 'Resume').replace(' ', '_').replace('.', '')
        
        return send_file(
            buffer, 
            as_attachment=True, 
            download_name=f"{name_for_file}_generated.pdf", 
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error during PDF generation: {e}")
        # In a real app, you might want a better error page
        return f"An error occurred during PDF generation: {e}", 500

if __name__ == '__main__':
    # This block is used only when running the script directly
    app.run(debug=True)
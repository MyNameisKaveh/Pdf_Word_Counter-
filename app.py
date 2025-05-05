import os
import uuid # To generate unique filenames
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from text_processor import process_text_file, initialize_nltk_on_server

# --- Configuration ---
UPLOAD_FOLDER = 'uploads' # Create this folder in your project directory
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB limit for uploads

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = 'your_very_secret_key_here' # Important for flashing messages

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- NLTK Initialization ---
# Attempt to initialize NLTK when the app starts.
# If it fails, the app might still run, but processing will fail later.
nltk_ready = initialize_nltk_on_server()
if not nltk_ready:
    print("WARNING: NLTK initialization failed. Text processing will not work.")
    # You could prevent the app from starting here if desired:
    # raise RuntimeError("NLTK failed to initialize. Cannot start application.")

# --- Helper Function ---
def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # --- File Upload Handling ---
        if not nltk_ready:
            flash('Server error: Text processing components are not ready.', 'danger')
            return render_template('index.html')

        if 'pdf_file' not in request.files:
            flash('No file part selected.', 'warning')
            return redirect(request.url)

        file = request.files['pdf_file']
        num_words_str = request.form.get('num_words', '100') # Get N, default 100

        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PDF.', 'danger')
            return redirect(request.url)

        try:
            num_words = int(num_words_str)
            if num_words < 1 or num_words > 1000: # Add reasonable limits for N
                 raise ValueError("Number of words out of range.")
        except ValueError:
            flash('Invalid number of words (must be between 1 and 1000).', 'danger')
            return redirect(request.url)


        if file:
            # Create a secure, unique filename
            # secure_filename removes potentially dangerous characters
            # uuid ensures no collisions even if users upload files with the same name
            filename_base = secure_filename(os.path.splitext(file.filename)[0])
            unique_id = uuid.uuid4().hex[:8] # Short unique ID
            filename = f"{filename_base}_{unique_id}.pdf"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(pdf_path)
                print(f"File saved to: {pdf_path}")

                # --- Process the saved file ---
                results = process_text_file(pdf_path, num_words)

                # --- Clean up the uploaded file ---
                try:
                    os.remove(pdf_path)
                    print(f"Removed temporary file: {pdf_path}")
                except OSError as e:
                    print(f"Error removing file {pdf_path}: {e}") # Log error, but continue

                # --- Display Results ---
                # Check if results indicate an error
                if results and results[0][0] in ["Error", "Info"]:
                    flash(f"{results[0][0]}: {results[0][1]}", 'danger' if results[0][0] == "Error" else 'info')
                    # Render index again, maybe without results table
                    return render_template('index.html')
                else:
                    # Success - render results template
                    return render_template('results.html', words=results, filename=file.filename)

            except Exception as e:
                # Catch potential errors during file save or processing call
                print(f"Error during file handling or processing: {e}")
                traceback.print_exc()
                flash(f'An unexpected error occurred: {e}', 'danger')
                 # Clean up if file was saved but processing failed
                if os.path.exists(pdf_path):
                    try: os.remove(pdf_path)
                    except OSError: pass
                return redirect(request.url) # Redirect back to upload form

    # --- GET Request: Show the upload form ---
    return render_template('index.html')

# --- Optional: Add a route to serve results if you keep them separate ---
# (Results are currently shown directly after POST)

# --- Run the App ---
if __name__ == '__main__':
    # Set debug=True for development (provides detailed errors, auto-reloads)
    # Set debug=False for production!
    # Use host='0.0.0.0' to make it accessible on your network (for testing)
    app.run(debug=True, host='0.0.0.0')

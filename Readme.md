حتماً! این یک پیش‌نویس برای فایل `README.md` پروژه شماست. می‌تونید اون رو کپی کنید و توی ریشه (root) ریپازیتوری گیت‌هابتون به عنوان فایل `README.md` قرار بدید.

**یادتون نره که `<your-username>` رو با نام کاربری واقعی خودتون در PythonAnywhere جایگزین کنید.**

```markdown
# PDF Most Frequent Words Analyzer

## Overview

This project is a web application designed to help users quickly identify the most frequently occurring words in an English-language PDF document. By providing a PDF file, users can obtain a list of the top N most common words (excluding common English stop words and after lemmatization), which can be particularly useful for pre-reading preparation of technical or specialized texts. This allows users to familiarize themselves with key terminology beforehand, potentially making the reading process smoother and more enjoyable.

The application is built with Python using the Flask framework for the backend and standard HTML/CSS for the frontend. Text extraction from PDFs is handled by PyMuPDF (fitz), and text processing (tokenization, lemmatization, stop word removal) is performed using NLTK.

**Live Application:** You can access the live web application here:
[http://Andolini1919.pythonanywhere.com/](http://Andolini1919.pythonanywhere.com/)
*(Replace `Andolini1919` with your actual PythonAnywhere username if it's different)*

## Features

*   **PDF Upload:** Users can upload PDF files directly through the web interface.
*   **Customizable Word Count:** Specify the number of top frequent words to display (e.g., top 100).
*   **Text Processing:**
    *   Extracts text content from PDF pages.
    *   Converts text to lowercase.
    *   Removes punctuation and digits.
    *   Tokenizes text into individual words.
    *   Lemmatizes words to their base form (e.g., "genes" becomes "gene").
    *   Filters out common English stop words.
*   **Frequency Analysis:** Counts the occurrences of the processed words.
*   **Results Display:** Shows a clear, ranked list of the most frequent words and their counts.

## Technologies Used

*   **Backend:**
    *   Python 3.10
    *   Flask (Web Framework)
    *   PyMuPDF (fitz) (PDF Text Extraction)
    *   NLTK (Natural Language Toolkit for text processing)
*   **Frontend:**
    *   HTML
    *   CSS (Basic styling)
*   **Deployment:**
    *   PythonAnywhere

## Project Structure

```
/Pdf_Word_Counter-/  (Your project root directory on PythonAnywhere)
├── app.py             # Main Flask application file
├── text_processor.py  # Module for PDF text extraction and NLTK processing
├── requirements.txt   # Python package dependencies
├── templates/
│   ├── index.html     # Upload form page
│   └── results.html   # Page to display results
├── uploads/           # Temporary storage for uploaded PDF files (server-side)
└── venv/              # Python virtual environment (not in Git repo)
```

## Setup and Installation (For Local Development or Alternative Deployment)

If you wish to run this project locally or deploy it to a different environment:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<YourGitHubUsername>/<YourRepositoryName>.git
    cd <YourRepositoryName>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLTK data:**
    Run the following command in your Python environment (or a Python script):
    ```bash
    python -m nltk.downloader wordnet punkt omw-1.4
    ```
    Alternatively, ensure the `initialize_nltk_on_server()` function in `text_processor.py` can download them or that they are pre-downloaded to a location NLTK can find (e.g., `~/nltk_data`).

5.  **Ensure the `uploads` directory exists:**
    ```bash
    mkdir uploads
    ```

6.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

## How to Use (Live Application)

1.  Navigate to [http://Andolini1919.pythonanywhere.com/](http://Andolini1919.pythonanywhere.com/).
2.  Click on "Choose File" (or similar) to select a PDF document from your device.
3.  Enter the desired number of top words to display in the "Number of words to find" field (default is 100).
4.  Click the "Process PDF" button.
5.  The results page will display the most frequent words and their counts from the uploaded PDF.

## Future Enhancements (Potential Ideas)

*   Support for other document formats (e.g., .txt, .docx).
*   Option to provide a custom list of stop words.
*   Ability to ignore specific words or phrases.
*   Visualization of word frequencies (e.g., word cloud).
*   Option to export the results (e.g., to CSV).
*   User accounts and history of processed files.
*   More robust error handling and user feedback.

## Contributing

Contributions are welcome! If you have suggestions for improvements or find any issues, please feel free to open an issue or submit a pull request.

## License

This project is open-source. (You can add a specific license like MIT if you wish).
```

**چند نکته:**

*   مطمئن شو که `<YourGitHubUsername>` و `<YourRepositoryName>` رو با اطلاعات واقعی ریپازیتوریت جایگزین کنی.
*   اگه از لایسنس خاصی استفاده می‌کنی (مثلا MIT License)، می‌تونی آخرش ذکر کنی.
*   می‌تونی بخش "Future Enhancements" رو بر اساس ایده‌های خودت کم و زیاد کنی.
*   این README برای پروژه‌ای که روی PythonAnywhere هست و کدش روی گیت‌هاب، مناسبه.

امیدوارم این README به دردت بخوره!

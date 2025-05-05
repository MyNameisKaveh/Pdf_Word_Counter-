# text_processor.py
import collections
import string
import re
import nltk
import traceback
import os # برای کار با مسیرها

# --- NLTK Data Setup (Server-Side Focus) ---
# Best Practice: Download NLTK data *once* during setup/deployment,
# rather than on every app start or request.
# You can run this manually in your server environment:
# python -m nltk.downloader wordnet punkt omw-1.4
# Or create a setup script.
# We will assume the data exists where NLTK expects it.

# Initialize lemmatizer globally, assuming data is present
lemmatizer = None

def initialize_nltk_on_server():
    """Initializes NLTK components needed, assuming data exists."""
    global lemmatizer
    if lemmatizer is None:
        try:
            # Verify data presence briefly before initializing
            print("Verifying NLTK data presence (wordnet, omw-1.4, punkt)...")
            nltk.data.find('corpora/wordnet')
            nltk.data.find('corpora/omw-1.4')
            nltk.data.find('tokenizers/punkt')
            print("NLTK data found. Initializing lemmatizer...")
            from nltk.stem import WordNetLemmatizer
            lemmatizer = WordNetLemmatizer()
            print("Lemmatizer initialized successfully on server.")
            return True
        except LookupError as e:
            print(f"ERROR: Required NLTK data not found: {e}. "
                  "Please run 'python -m nltk.downloader wordnet punkt omw-1.4' "
                  "in your server environment before starting the Flask app.")
            return False
        except Exception as e:
            print(f"ERROR during NLTK initialization: {e}")
            traceback.print_exc()
            return False

# --- STOP_WORDS List (Unchanged) ---
STOP_WORDS = set([
    # Standard English stop words... (کامل لیست مثل قبل)
    "a", "an", "the", # ... ( بقیه کلمات مثل نسخه قبل) ...
    # Words still considered non-content or noise...
    "et", "al", "fig", "figure", "table", "page", "vol", "no", "journal", # ...
    # Single letters...
    "b", "c", "d", # ...
])

def process_text_file(pdf_path: str, n_words: int = 100) -> list:
    """
    Processes a PDF file located at pdf_path to find the most frequent words.

    Args:
        pdf_path: The full path to the uploaded PDF file on the server.
        n_words: The number of most frequent words to return.

    Returns:
        A list of tuples (word, frequency), sorted by frequency.
        Returns an error message list if processing fails.
    """
    global lemmatizer
    if lemmatizer is None:
        print("ERROR: Lemmatizer not initialized. Cannot process.")
        # You might want to raise an exception or handle this more robustly
        return [("Error", "Server NLTK components not ready.")]

    try:
        # --- 1. Extract Text using PyMuPDF ---
        import fitz # PyMuPDF
        print(f"Processing file: {pdf_path}")
        doc = fitz.open(pdf_path)
        raw_text = ""
        for page in doc:
            raw_text += page.get_text("text")
        doc.close()
        print(f"Extracted text length: {len(raw_text)} characters")
        if not raw_text.strip():
            return [("Info", "No text could be extracted from the PDF.")]

        # --- 2. Cleaning, Tokenizing, Lemmatizing (Code is the same as before) ---
        text_lower = raw_text.lower()
        text_no_urls = re.sub(r'https?://\S+|www\.\S+|doi[:/]\S+|\b\w+/\w+\b', '', text_lower)
        text_no_digits = re.sub(r'\d+', '', text_no_urls)
        text_almost_clean = re.sub(r"[^a-z\s']", '', text_no_digits)
        text_clean = re.sub(r'\s+', ' ', text_almost_clean).strip()

        tokens = nltk.word_tokenize(text_clean)

        lemmatized_words = []
        for word in tokens:
            cleaned_word = word.rstrip("'s") if word.endswith("'s") else word
            cleaned_word = cleaned_word.strip("'")
            if not cleaned_word: continue

            lemma = lemmatizer.lemmatize(cleaned_word, pos='n')
            if lemma == cleaned_word:
                 lemma = lemmatizer.lemmatize(cleaned_word, pos='v')

            if lemma not in STOP_WORDS and 2 < len(lemma) < 25:
                lemmatized_words.append(lemma)

        if not lemmatized_words:
            print("No significant words found after filtering.")
            return []

        # --- 3. Counting ---
        word_counts = collections.Counter(lemmatized_words)
        most_common = word_counts.most_common(n_words)

        print(f"Found {len(most_common)} frequent words.")
        return most_common

    except fitz.fitz.FileNotFoundError:
        print(f"ERROR: PDF file not found at path: {pdf_path}")
        return [("Error", "PDF file disappeared or path is incorrect.")]
    except Exception as e:
        print(f"Error during PDF processing: {e}")
        traceback.print_exc()
        return [("Error processing PDF", str(e))]

# text_processor.py
import collections
import string
import re
import nltk
import traceback
import os 
import nltk.data

# --- NLTK Data Setup & Initialization ---
lemmatizer = None
def initialize_nltk_on_server():
    """Initializes NLTK components needed, assuming data exists."""
    global lemmatizer

    user_nltk_data_path = '/home/Andolini1919/nltk_data' 
    if user_nltk_data_path not in nltk.data.path:
        print(f"Adding path to NLTK search paths: {user_nltk_data_path}")
        nltk.data.path.append(user_nltk_data_path)
    else:
        print(f"Path {user_nltk_data_path} already in nltk.data.path")

    if lemmatizer is None:
        try:
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
            print(f"ERROR: Required NLTK data not found even after adding path: {e}. "
                  f"Check if data was downloaded correctly to '{user_nltk_data_path}'.")
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"ERROR during NLTK initialization: {e}")
            traceback.print_exc()
            return False
    else:
        return True

# --- STOP_WORDS List (کامل مثل قبل) ---
STOP_WORDS = set([
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "as",
    "is", "am", "are", "was", "were", "be", "being", "been",
    "it", "its", "it's", "i", "you", "he", "she", "they", "we", "my", "your",
    "his", "her", "their", "our", "me", "him", "her", "them", "us",
    "and", "or", "but", "so", "if", "because", "while", "since",
    "this", "that", "these", "those", "which", "who", "whom",
    "also", "just", "not", "no", "very", "can", "will", "shall", "may", "might",
    "must", "would", "could", "should", "has", "have", "had", "do", "does", "did",
    "from", "up", "down", "out", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "than", "too",
    "et", "al", "fig", "figure", "table", "page", "vol", "no", "journal", "university",
    "pubmed", "doi", "org", "http", "https", "www", "author", "authors", "article",
    "abstract", "introduction", "discussion", "conclusion", "conclusions",
    "reference", "references", "acknowledgement", "acknowledgements", "supplementary",
    "however", "therefore", "thus", "hence", "although", "though",
    "within", "without", "among", "between",
    "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
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
    # Check lemmatizer status
    if lemmatizer is None:
        if not initialize_nltk_on_server():
             print("ERROR: Lemmatizer is still not initialized during processing.")
             return [("Error", "Server NLTK components are not ready (failed again).")]

    # --- !!! Import fitz BEFORE the try block !!! ---
    import fitz # PyMuPDF
    # -----------------------------------------------

    try:
        # --- 1. Extract Text using PyMuPDF ---
        # import fitz is now moved above
        print(f"Processing file: {pdf_path}")
        doc = fitz.open(pdf_path) # Now 'fitz' is guaranteed to be defined
        raw_text = ""
        for page in doc:
            raw_text += page.get_text("text")
        doc.close()
        print(f"Extracted text length: {len(raw_text)} characters")
        if not raw_text.strip():
            return [("Info", "No text could be extracted from the PDF.")]

        # --- 2. Cleaning, Tokenizing, Lemmatizing ---
        text_lower = raw_text.lower()
        text_no_urls = re.sub(r'https?://\S+|www\.\S+|doi[:/]\S+|\b\w+/\w+\b', '', text_lower)
        text_no_digits = re.sub(r'\d+', '', text_no_urls)
        text_almost_clean = re.sub(r"[^a-z\s']", '', text_no_digits)
        text_clean = re.sub(r'\s+', ' ', text_almost_clean).strip()

        try:
            tokens = nltk.word_tokenize(text_clean)
        except Exception as tokenize_error:
             print(f"NLTK tokenization failed: {tokenize_error}. Falling back to simple split.")
             tokens = text_clean.split() # Fallback

        lemmatized_words = []
        for word in tokens:
            cleaned_word = word.rstrip("'s") if word.endswith("'s") else word
            cleaned_word = cleaned_word.strip("'")
            if not cleaned_word: continue

            if lemmatizer:
                lemma = lemmatizer.lemmatize(cleaned_word, pos='n')
                if lemma == cleaned_word:
                     lemma = lemmatizer.lemmatize(cleaned_word, pos='v')
            else:
                print("Warning: Lemmatizer object is None during processing loop.")
                lemma = cleaned_word # Fallback

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

    # Now these except blocks work correctly because 'fitz' is defined
    except fitz.fitz.FileNotFoundError:
        print(f"ERROR: PDF file not found at path: {pdf_path}")
        return [("Error", "PDF file disappeared or path is incorrect.")]
    except Exception as e:
        print(f"Error during PDF processing: {e}")
        traceback.print_exc() # Ensure traceback is imported in app.py for this to work if error bubbles up
        # More specific error message if possible
        if "cannot open broken document" in str(e).lower():
             return [("Error processing PDF", "The PDF file seems to be corrupted or broken.")]
        else:
             return [("Error processing PDF", str(e))]

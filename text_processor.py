# text_processor.py
import collections
import string
import re
import nltk
import traceback # For detailed error logging

# --- NLTK Setup within Pyodide Environment ---
def download_nltk_data():
    """
    Attempts to download necessary NLTK data (corpora).
    NLTK's download function should handle already existing data gracefully.
    Uses raise_on_error=True for clearer feedback if download fails.
    """
    required_corpora = ['wordnet', 'omw-1.4', 'punkt']
    print("Attempting to ensure NLTK data is available...")
    all_downloaded = True
    for corpus in required_corpora:
        try:
            print(f"Downloading/Verifying NLTK data: {corpus}...")
            # Directly attempt download. raise_on_error=True will throw exception on failure.
            # quiet=False helps see progress in browser console during development.
            # Set quiet=True in production if downloads are reliable.
            success = nltk.download(corpus, quiet=False, raise_on_error=True)
            if success:
                 print(f"NLTK data '{corpus}' is available.")
            else:
                 # This part might not be reached if raise_on_error=True works
                 print(f"NLTK download command returned False for '{corpus}'. Verification needed.")
                 all_downloaded = False # Mark as potentially failed

        except Exception as e:
            # Catch any exception during download (network, permissions, etc.)
            print(f"ERROR downloading NLTK data '{corpus}': {e}")
            traceback.print_exc() # Print full traceback for debugging in browser console
            all_downloaded = False

    if all_downloaded:
        print("All required NLTK data download attempts initiated.")
    else:
        print("WARNING: One or more NLTK data packages failed to download/initiate.")

    # --- Final Verification Step ---
    # It's still good practice to verify if NLTK can now find the data
    print("Verifying NLTK data presence via nltk.data.find...")
    final_check_ok = True
    for corpus in required_corpora:
         try:
             # Determine the correct subdirectory ('corpora' or 'tokenizers')
             path_type = 'tokenizers' if corpus == 'punkt' else 'corpora'
             nltk.data.find(f'{path_type}/{corpus}')
             print(f"Verified: '{corpus}' found by NLTK.")
         except LookupError:
             # Use the correct exception here!
             print(f"ERROR: Verification failed. NLTK data '{corpus}' still not found after download attempt.")
             final_check_ok = False
         except Exception as e_find:
             # Catch any other unexpected error during find
             print(f"ERROR during verification find for '{corpus}': {e_find}")
             final_check_ok = False

    if final_check_ok:
         print("Final NLTK data verification successful.")
         return True # Indicate success
    else:
         print("ERROR: Final NLTK data verification failed for one or more packages.")
         return False # Indicate failure
# --------------------------------------------

# Initialize the lemmatizer
lemmatizer = None

def initialize_lemmatizer():
    """Initializes the WordNetLemmatizer if not already done and data is present."""
    global lemmatizer
    if lemmatizer is None:
        try:
            # Explicitly check if required data is findable before initializing
            print("Checking for WordNet data before initializing lemmatizer...")
            nltk.data.find('corpora/wordnet')
            nltk.data.find('corpora/omw-1.4') # Often needed by WordNet
            print("WordNet data found. Initializing lemmatizer...")
            # Now import and initialize
            from nltk.stem import WordNetLemmatizer
            lemmatizer = WordNetLemmatizer()
            print("Lemmatizer initialized successfully.")
        except LookupError:
            # Catch the correct error if data is missing
            print("ERROR: Cannot initialize lemmatizer because WordNet/OMW-1.4 data is missing or not found by NLTK.")
        except Exception as e:
            # Catch other potential errors during import or initialization
            print(f"Error initializing lemmatizer: {e}")
            traceback.print_exc()


# --- STOP_WORDS List (Unchanged from previous version) ---
STOP_WORDS = set([
    # Standard English stop words
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

    # Words still considered non-content or noise
    "et", "al", "fig", "figure", "table", "page", "vol", "no", "journal", "university",
    "pubmed", "doi", "org", "http", "https", "www", "author", "authors", "article",
    "abstract", "introduction", "discussion", "conclusion", "conclusions",
    "reference", "references", "acknowledgement", "acknowledgements", "supplementary",
    "however", "therefore", "thus", "hence", "although", "though",
    "within", "without", "among", "between",

    # Single letters
    "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
])


def process_text(raw_text: str, n_words: int = 100) -> list:
    """
    Processes the raw text: cleans, tokenizes, lemmatizes, removes stop words,
    and counts the frequency of the remaining words.
    """
    global lemmatizer
    if not raw_text:
        return []

    # Ensure lemmatizer is initialized - crucial check!
    if lemmatizer is None:
        print("Lemmatizer is not initialized. Attempting to initialize now...")
        initialize_lemmatizer()
        # If still None after trying again, we cannot proceed.
        if lemmatizer is None:
             print("ERROR: Lemmatizer failed to initialize. Cannot process text.")
             return [("Error", "Lemmatizer initialization failed. Check NLTK data download status in console.")]

    try:
        # --- Text Cleaning (mostly unchanged) ---
        text_lower = raw_text.lower()
        text_no_urls = re.sub(r'https?://\S+|www\.\S+|doi[:/]\S+|\b\w+/\w+\b', '', text_lower)
        text_no_digits = re.sub(r'\d+', '', text_no_urls)
        text_almost_clean = re.sub(r"[^a-z\s']", '', text_no_digits)
        text_clean = re.sub(r'\s+', ' ', text_almost_clean).strip()

        # --- Tokenization ---
        try:
            tokens = nltk.word_tokenize(text_clean)
        except Exception as tokenize_error:
             print(f"NLTK tokenization failed: {tokenize_error}. Falling back to simple split.")
             tokens = text_clean.split() # Fallback

        # --- Lemmatization and Filtering ---
        lemmatized_words = []
        for word in tokens:
            cleaned_word = word.rstrip("'s") if word.endswith("'s") else word
            cleaned_word = cleaned_word.strip("'")
            if not cleaned_word: continue

            # Lemmatize
            lemma = lemmatizer.lemmatize(cleaned_word, pos='n')
            if lemma == cleaned_word:
                 lemma = lemmatizer.lemmatize(cleaned_word, pos='v')

            # Filter stop words and short/long words
            if lemma not in STOP_WORDS and 2 < len(lemma) < 25:
                lemmatized_words.append(lemma)

        if not lemmatized_words:
            print("No significant words found after filtering.")
            return []

        # --- Counting ---
        word_counts = collections.Counter(lemmatized_words)
        most_common = word_counts.most_common(n_words)

        return most_common

    except Exception as e:
        print(f"Error during Python text processing: {e}")
        traceback.print_exc()
        return [("Error processing text", str(e))]

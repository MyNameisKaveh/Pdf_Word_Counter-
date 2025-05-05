# text_processor.py
import collections
import string
import re
# Import NLTK for lemmatization and tokenization
import nltk

# --- NLTK Setup within Pyodide Environment ---
# This setup needs to be run *once* after NLTK is loaded in Pyodide.
# We'll trigger this from JavaScript after loading NLTK package.
def download_nltk_data():
    """Downloads necessary NLTK data (corpora) if not already present."""
    required_corpora = ['wordnet', 'omw-1.4', 'punkt']
    for corpus in required_corpora:
        try:
            # Check if the corpus path exists
            nltk.data.find(f'corpora/{corpus}' if corpus != 'punkt' else f'tokenizers/{corpus}')
        except nltk.downloader.DownloadError:
            print(f"Downloading NLTK data: {corpus}...")
            # Download quietly to avoid excessive console output in browser
            nltk.download(corpus, quiet=True)
        except LookupError: # Handle cases where find might raise LookupError
             print(f"NLTK data lookup error for: {corpus}. Attempting download...")
             nltk.download(corpus, quiet=True)
    print("NLTK data ready.")
# --------------------------------------------

# Initialize the lemmatizer (needs WordNet data)
# We'll initialize it properly after ensuring data is downloaded.
lemmatizer = None

def initialize_lemmatizer():
    """Initializes the WordNetLemmatizer if not already done."""
    global lemmatizer
    if lemmatizer is None:
        try:
            from nltk.stem import WordNetLemmatizer
            lemmatizer = WordNetLemmatizer()
            print("Lemmatizer initialized.")
        except Exception as e:
            print(f"Error initializing lemmatizer: {e}")

# --- Updated STOP_WORDS List ---
# Common/Generic words related to research structure/process are NOT included here
# to allow them to appear in the results if frequent.
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

    # Words still considered non-content or noise (KEEP removing these)
    "et", "al",             # Citation markers
    "fig", "figure", "table", "page", "vol", "no", # Document structure/references
    "journal", "university", "pubmed", "doi", "org", "http", "https", "www", # Publication/Web related
    "author", "authors", "article", "abstract", "introduction", # Section titles (often frequent noise)
    "discussion", "conclusion", "conclusions", "reference", "references", # Section titles
    "acknowledgement", "acknowledgements", "supplementary", # Section titles
    "however", "therefore", "thus", "hence", "although", "though", # Discourse markers
    "within", "without", "among", "between", # Common prepositions/adverbs

    # Single letters (often noise after cleaning)
    "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
])

def process_text(raw_text: str, n_words: int = 100) -> list:
    """
    Processes the raw text: cleans, tokenizes, lemmatizes, removes stop words,
    and counts the frequency of the remaining words.

    Args:
        raw_text: The entire text content as a single string.
        n_words: The number of most frequent words to return.

    Returns:
        A list of tuples (word, frequency), sorted by frequency.
        Returns an error message list if processing fails.
    """
    global lemmatizer
    if not raw_text:
        return []

    # Ensure lemmatizer is initialized (it should be after NLTK setup)
    if lemmatizer is None:
        initialize_lemmatizer()
        # If still None after trying to initialize, return error
        if lemmatizer is None:
             return [("Error", "Lemmatizer could not be initialized. NLTK data might be missing.")]

    try:
        # 1. Basic Cleaning (Lowercasing, remove URLs/DOIs like patterns first)
        text_lower = raw_text.lower()
        # Regex to remove URLs/DOIs and paths (adjust if too aggressive)
        # Matches http/https/www, doi patterns, and simple word/word paths
        text_no_urls = re.sub(r'https?://\S+|www\.\S+|doi[:/]\S+|\b\w+/\w+\b', '', text_lower)

        # Remove numbers - Decide whether to remove all digits or just standalone numbers
        # text_no_digits = re.sub(r'\b\d+\b', '', text_no_urls) # Removes only standalone numbers
        text_no_digits = re.sub(r'\d+', '', text_no_urls) # Removes digits potentially attached to words too

        # 2. Remove punctuation (more carefully)
        # Keep internal apostrophes for now, remove other punctuation
        # Allows letters (a-z) and apostrophes within words, removes others except space
        text_almost_clean = re.sub(r"[^a-z\s']", '', text_no_digits)
        # Replace multiple spaces with single space and trim ends
        text_clean = re.sub(r'\s+', ' ', text_almost_clean).strip()

        # 3. Tokenize using NLTK (handles contractions better than split)
        try:
            tokens = nltk.word_tokenize(text_clean)
        except Exception as tokenize_error:
             # If tokenization fails (e.g., resource not found), fallback or raise
             print(f"NLTK tokenization failed: {tokenize_error}. Falling back to simple split.")
             # Fallback to simple split - might be less accurate
             tokens = text_clean.split()


        # 4. Lemmatize and Filter
        lemmatized_words = []
        for word in tokens:
            # Handle potential apostrophes (e.g., from 's) before lemmatizing
            # Simple approach: remove trailing 's if it exists
            cleaned_word = word.rstrip("'s") if word.endswith("'s") else word
            # Remove any remaining leading/trailing apostrophes if any slipped through
            cleaned_word = cleaned_word.strip("'")

            # Skip if the word is now empty after cleaning
            if not cleaned_word:
                continue

            # Lemmatize (get the base form of the word)
            # Try noun form first, then verb form if no change
            lemma = lemmatizer.lemmatize(cleaned_word, pos='n')
            if lemma == cleaned_word: # If no change as noun, try as verb
                 lemma = lemmatizer.lemmatize(cleaned_word, pos='v')

            # Filter stop words and short words AFTER lemmatization
            # Only keep words longer than 2 characters that are not stop words
            if lemma not in STOP_WORDS and len(lemma) > 2:
                # Optional: Filter excessively long words (potential errors from bad PDF extraction)
                if len(lemma) < 25: # Arbitrary limit, adjust if needed
                    lemmatized_words.append(lemma)

        if not lemmatized_words:
            print("No significant words found after filtering.")
            return []

        # 5. Count word frequencies
        word_counts = collections.Counter(lemmatized_words)

        # 6. Get the N most common words
        most_common = word_counts.most_common(n_words)

        return most_common

    except Exception as e:
        # Catch any unexpected error during processing
        import traceback
        print(f"Error during Python text processing: {e}")
        print(traceback.format_exc()) # Print stack trace for debugging
        # Return error info formatted as a list of tuples for consistency
        return [("Error processing text", str(e))]

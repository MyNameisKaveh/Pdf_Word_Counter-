# text_processor.py
import collections
import string
import re

# Define a set of common English stop words
# You can expand this list for better results
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
    "few", "more", "most", "other", "some", "such", "than", "too", "using",
    # Consider adding more domain-specific words if needed, or common short words
    "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
])

def process_text(raw_text: str, n_words: int = 100) -> list:
    """
    Processes the raw text extracted from a PDF to find the most frequent words.

    Args:
        raw_text: The entire text content from the PDF as a single string.
        n_words: The number of most frequent words to return.

    Returns:
        A list of tuples, where each tuple contains a word and its frequency count,
        sorted by frequency in descending order. Returns an empty list if text is empty.
        Returns an error message string if processing fails.
    """
    if not raw_text:
        return [] # Return empty list if no text was provided

    try:
        # 1. Convert to lowercase
        text_lower = raw_text.lower()

        # 2. Remove punctuation
        # Create a translation table to remove all punctuation characters
        translator = str.maketrans('', '', string.punctuation)
        text_no_punct = text_lower.translate(translator)

        # 3. Remove digits (optional, uncomment if needed)
        text_no_digits = re.sub(r'\d+', '', text_no_punct)

        # 4. Tokenize: Split the text into a list of words based on whitespace
        words = text_no_digits.split()

        # 5. Filter stop words and short words (e.g., single letters)
        filtered_words = [
            word for word in words
            if word not in STOP_WORDS and len(word) > 1 # Keep words longer than 1 char
        ]

        if not filtered_words:
            return [] # Return empty list if only stop words/short words were present

        # 6. Count word frequencies
        word_counts = collections.Counter(filtered_words)

        # 7. Get the N most common words
        most_common = word_counts.most_common(n_words)

        return most_common

    except Exception as e:
        # Log the error for debugging if possible (difficult in pure frontend)
        # Return an error indicator to the JavaScript caller
        print(f"Error during Python text processing: {e}")
        # You might want to return a specific error format JS can check
        # For now, returning the error message itself:
        return [("Error processing text", str(e))]

# You can add a small test block here if you run this file directly
# if __name__ == '__main__':
#     sample_text = "This is a Sample text, with sample words. Text processing is fun! 123 numbers."
#     top_words = process_text(sample_text, 5)
#     print(top_words) # Expected: [('sample', 2), ('text', 2), ('words', 1), ('processing', 1), ('fun', 1)]

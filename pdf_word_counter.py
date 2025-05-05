# -*- coding: utf-8 -*-
"""
PDF Word Frequency Counter

This script extracts text from a given PDF file, cleans the text,
removes common English stop words, counts the frequency of the remaining words,
and prints the N most frequent words.
"""

import fitz  # PyMuPDF library for PDF processing
import collections
import string
import re
import argparse # For handling command-line arguments
import os # For checking if file exists

# --- Constants ---

# A basic set of English stop words.
# Consider using a more comprehensive list from libraries like NLTK or spaCy for better results.
STOP_WORDS = set([
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "as",
    "is", "am", "are", "was", "were", "be", "being", "been",
    "it", "its", "it's", "i", "you", "he", "she", "they", "we", "my", "your",
    "his", "her", "their", "our", "me", "him", "her", "them", "us",
    "and", "or", "but", "so", "if", "because", "while", "since",
    "this", "that", "these", "those",
    "also", "just", "not", "no", "very", "can", "will", "shall", "may", "might",
    "must", "would", "could", "should",
    "from", "up", "down", "out", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "page", "figure", "table",
    # Single letters (can often appear after cleaning)
    "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n",
    "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
])

# --- Core Functions ---

def extract_text_from_pdf(pdf_path):
    """
    Extracts plain text content from all pages of a PDF file.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        str: The concatenated text content of the PDF, or None if an error occurs.
    """
    full_text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            full_text += page.get_text("text")
        doc.close()
        print(f"Successfully extracted text from '{os.path.basename(pdf_path)}'.")
        return full_text
    except Exception as e:
        print(f"Error opening or reading PDF file '{pdf_path}': {e}")
        return None

def clean_and_tokenize(text):
    """
    Cleans the text by converting to lowercase, removing punctuation and digits,
    and then tokenizes the text into a list of words.

    Args:
        text (str): The raw text string.

    Returns:
        list: A list of cleaned words (tokens).
    """
    if not text:
        return []

    # 1. Convert to lowercase
    text_lower = text.lower()

    # 2. Remove punctuation
    # Create a translation table to remove all punctuation characters
    translator = str.maketrans('', '', string.punctuation)
    text_no_punct = text_lower.translate(translator)

    # 3. Remove digits (optional, uncomment if needed)
    # text_no_digits = re.sub(r'\d+', '', text_no_punct)
    text_to_split = text_no_punct # Use this if you want to keep digits as words
    # text_to_split = text_no_digits # Use this if you want to remove digits

    # 4. Tokenize (split into words)
    words = text_to_split.split()

    print(f"Text cleaned. Initial word count (before stop word removal): {len(words)}")
    return words

def filter_stop_words(word_list, stop_words_set):
    """
    Removes stop words and short words (<= 1 character) from a list of words.

    Args:
        word_list (list): The list of words to filter.
        stop_words_set (set): A set containing the stop words to remove.

    Returns:
        list: A list of words with stop words removed.
    """
    filtered = [
        word for word in word_list
        if word not in stop_words_set and len(word) > 1 # Keep words longer than 1 char
    ]
    print(f"Stop words removed. Word count: {len(filtered)}")
    return filtered

def count_word_frequency(word_list):
    """
    Counts the frequency of each word in a list.

    Args:
        word_list (list): The list of words to count.

    Returns:
        collections.Counter: A Counter object mapping words to their frequencies.
    """
    return collections.Counter(word_list)

# --- Main Execution Logic ---

def main():
    """
    Main function to parse arguments, run the analysis, and print results.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF and count the frequency of the most common words."
    )
    parser.add_argument(
        "pdf_filepath",
        help="Path to the input PDF file."
    )
    parser.add_argument(
        "-n", "--num_words",
        type=int,
        default=100,
        help="The number of most frequent words to display (default: 100)."
    )
    parser.add_argument(
        "--min_len",
        type=int,
        default=2, # Default minimum word length after cleaning
        help="Minimum length of words to consider after cleaning (default: 2)."
    )

    # Parse command-line arguments
    args = parser.parse_args()

    pdf_path = args.pdf_filepath
    top_n = args.num_words
    min_word_length = args.min_len # Store min length although filter_stop_words currently uses >1

    # --- Workflow ---
    print(f"Processing PDF: {pdf_path}")
    print(f"Finding top {top_n} words (min length {min_word_length}).")

    # 1. Check if file exists
    if not os.path.exists(pdf_path):
      print(f"Error: File not found at '{pdf_path}'")
      return # Exit if file doesn't exist

    # 2. Extract text
    raw_text = extract_text_from_pdf(pdf_path)
    if raw_text is None:
        return # Exit if text extraction failed

    # 3. Clean and tokenize text
    all_words = clean_and_tokenize(raw_text)
    if not all_words:
        print("No words found after cleaning.")
        return

    # 4. Filter stop words
    # We update the filter to use min_word_length from args if desired,
    # but the current filter_stop_words uses len(word) > 1 hardcoded.
    # Let's modify filter_stop_words slightly or add the check here.
    # For simplicity, let's stick to len(word) > 1 in filter_stop_words
    # but acknowledge the parameter exists for future enhancement.
    meaningful_words = filter_stop_words(all_words, STOP_WORDS)
    if not meaningful_words:
        print("No meaningful words found after removing stop words.")
        return

    # 5. Count word frequency
    word_counts = count_word_frequency(meaningful_words)

    # 6. Get the most common words
    most_common = word_counts.most_common(top_n)

    # 7. Print the results
    print(f"\n--- Top {top_n} Most Frequent Words in '{os.path.basename(pdf_path)}' ---")
    if most_common:
        # Find the longest word for alignment
        max_word_len = max(len(word) for word, count in most_common)
        # Find the widest count string for alignment
        max_count_len = max(len(str(count)) for word, count in most_common)

        for i, (word, count) in enumerate(most_common):
            # Use f-string alignment: < left-align, > right-align
            print(f"{i+1:>3}. {word:<{max_word_len}} : {count:>{max_count_len}}")
    else:
        print("No words found to display.")

    print("-" * (len(f"--- Top {top_n} Most Frequent Words in '{os.path.basename(pdf_path)}' ---") + 2)) # Separator line


# Make sure the main function runs only when the script is executed directly
if __name__ == "__main__":
    main()

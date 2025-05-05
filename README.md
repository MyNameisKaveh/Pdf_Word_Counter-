# PDF Word Frequency Counter

A simple Python script to extract text from a PDF file, process it, and identify the most frequently occurring words. This is useful for quickly understanding the key terms in a document, especially technical books or papers, before reading them in detail.

## Features

*   Extracts text content from standard PDF files (text-based, not image-based PDFs).
*   Cleans text by converting to lowercase and removing punctuation.
*   Removes common English stop words.
*   Counts the frequency of remaining words.
*   Displays the top N most frequent words (configurable).
*   Command-line interface for ease of use.

## Requirements

*   Python 3.6+
*   Libraries listed in `requirements.txt` (`PyMuPDF`)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```
2.  **Install required libraries:**
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Then install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script from your terminal, providing the path to the PDF file. You can optionally specify the number of top words to display.

```bash
python pdf_word_counter.py <path_to_your_pdf_file.pdf> [options]

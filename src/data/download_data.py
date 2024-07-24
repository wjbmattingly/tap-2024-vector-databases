import json
import requests
from bs4 import BeautifulSoup
import random
from tqdm import tqdm
import chardet

def extract_main_text(url):
    """
    Extract the main text content from a given URL, removing footnote references
    and preserving paragraph separations. Handles character encoding issues.
    
    Args:
    url (str): The URL of the webpage to extract text from.
    
    Returns:
    str: The extracted main text content, or an error message if extraction fails.
    """
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        return f"Failed to retrieve the webpage. Status code: {response.status_code}"

    # Detect the encoding of the response content
    detected_encoding = chardet.detect(response.content)['encoding']

    # Parse the HTML content with the detected encoding
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=detected_encoding)

    # Find the main content div
    main_content = soup.find('div', class_='innerdiv docbody')

    if not main_content:
        return "Could not find the main content"

    # Replace footnote reference links with a special marker
    for a in main_content.find_all('a', class_='ptr'):
        a.replace_with('FOOTNOTE_MARKER')

    # Extract all paragraph texts, preserving separations
    paragraphs = main_content.find_all('p')
    
    # Process each paragraph separately
    processed_paragraphs = []
    for p in paragraphs:
        # Get text, replace footnote markers, and clean whitespace
        text = p.get_text(strip=True)
        text = text.replace('FOOTNOTE_MARKER', ' ')
        text = ' '.join(word for word in text.split() if word)
        processed_paragraphs.append(text)
    
    # Join paragraphs with linebreaks
    main_text = '\n'.join(processed_paragraphs)

    return main_text

def load_metadata(file_path="data/raw/founders-online-metadata.json"):
    """
    Load metadata from a JSON file.
    
    Args:
    file_path (str): Path to the JSON file containing metadata.
    
    Returns:
    list: List of metadata items.
    """
    with open(file_path, "r") as f:
        return json.load(f)

def download(randomize=True, max_items=1000, seed=42):
    """
    Download and process a subset of items from the metadata.
    
    Args:
    randomize (bool): Whether to randomize the selection of items.
    max_items (int): Maximum number of items to process.
    seed (int): Random seed for reproducibility.
    
    Returns:
    None
    """
    # Load the metadata
    data = load_metadata()
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Create a subset of the data
    if randomize:
        subset = random.sample(data, min(max_items, len(data)))
    else:
        subset = data[:max_items]
    
    # Process each item in the subset
    for item in tqdm(subset):
        item["content"] = extract_main_text(item["permalink"])
    
    # Save the processed data
    output_file = f"data/processed/sample_{max_items}_{seed}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(subset, f, indent=2, ensure_ascii=False)
    
    print(f"Processed data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    download(randomize=True, max_items=1000, seed=42)
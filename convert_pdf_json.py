import fitz # PyMuPDF
import json
import os

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    extracted_text = []
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        extracted_text.append(page.get_text())
    
    doc.close()
    return extracted_text

def structure_text_to_json(text_list, metadata):
    """
    Converts extracted text into a structured JSON format.
    Customize this function based on the structure you want for your JSON.
    
    :param text_list: List of text extracted from each page of the PDF.
    :param metadata: Dictionary containing metadata about the research paper.
    :return: Structured JSON object.
    """
    json_data = {
        "metadata": metadata,  # Metadata like title, authors, etc.
        "content": []  # Content broken down by pages or sections
    }
    
    for i, text in enumerate(text_list):
        json_data["content"].append({
            "page": i + 1,
            "text": text.strip()
        })
    
    return json_data

def save_json(json_data, output_path):
    """Saves JSON data to a file."""
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

def process_pdf_to_json(pdf_path, output_dir):
    """Main function to process a PDF file and save its content as a JSON file."""
    # Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_path)
    
    # Collect metadata (customize this part based on your requirements)
    metadata = {
        "file name": pdf_path
    }
    
    # Structure text and metadata into JSON format
    structured_data = structure_text_to_json(extracted_text, metadata)
    
    # Define output JSON file path
    base_filename = os.path.basename(pdf_path).replace('.pdf', '.json')
    output_path = os.path.join(output_dir, base_filename)
    
    # Save JSON to file
    save_json(structured_data, output_path)
    print(f"JSON saved at: {output_path}")

if __name__ == "__main__":
    # Example usage
    paths=list()
    for dirname, _, filenames in os.walk('/mnt/rds/redhen/gallina/home/rks110/frame_and_papers/'):
        for filename in filenames:
            if filename[-4:]==".pdf":
                paths.append(filename)
        
        
    #pdf_path = "Divjak_CxGBERT_2020.coling-main.355.pdf"  # Path to your PDF file
    output_dir = "./output_jsons"  # Directory to save JSON files
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process PDF and save to JSON
    for pdf_path in paths:
        process_pdf_to_json(pdf_path, output_dir)


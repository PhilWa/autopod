import os
from openai import OpenAI
from typing import List, Optional
import PyPDF2
from tqdm import tqdm
from dotenv import load_dotenv

from config_parser import (
    load_config,
    get_models,
    get_directories,
    format_distillation_prompt,
)


def validate_pdf(file_path: str) -> bool:
    """Validate if file exists and is a PDF."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return False
    if not file_path.lower().endswith(".pdf"):
        print("Error: File is not a PDF")
        return False
    return True


def get_pdf_metadata(file_path: str) -> Optional[dict]:
    """Extract metadata from PDF file."""
    if not validate_pdf(file_path):
        return None

    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = {
                "num_pages": len(pdf_reader.pages),
                "metadata": pdf_reader.metadata,
            }
            return metadata
    except Exception as e:
        print(f"Error extracting metadata: {str(e)}")
        return None


def extract_text_from_pdf(file_path: str, max_chars: int = 100000) -> Optional[str]:
    """Extract text content from PDF file."""
    if not validate_pdf(file_path):
        return None

    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"Processing PDF with {num_pages} pages...")

            extracted_text = []
            total_chars = 0

            for page_num in tqdm(range(num_pages), desc="Extracting pages"):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if total_chars + len(text) > max_chars:
                    remaining_chars = max_chars - total_chars
                    extracted_text.append(text[:remaining_chars])
                    print(
                        f"\nReached {max_chars} character limit at page {page_num + 1}"
                    )
                    break

                extracted_text.append(text)
                total_chars += len(text)

            final_text = "\n".join(extracted_text)
            print(f"\nExtraction complete! Total characters: {len(final_text)}")
            return final_text

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def create_chunks(text: str, chunk_size: int) -> List[str]:
    """Split text into chunks at word boundaries."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 for space
        if current_length + word_length > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def process_chunk(client: OpenAI, chunk: str, chunk_num: int, config) -> str:
    """Process a single chunk of text."""
    models = get_models(config)

    messages = format_distillation_prompt(config, chunk)

    try:
        response = client.chat.completions.create(
            model=models["content_distillation"]["model"],
            messages=messages,
            temperature=models["content_distillation"]["temperature"],
            max_tokens=models["content_distillation"]["max_tokens"],
        )

        processed_text = response.choices[0].message.content.strip()

        print(f"\n{'='*40} Chunk {chunk_num} {'='*40}")
        print(f"INPUT TEXT:\n{chunk[:500]}...")
        print(f"\nPROCESSED TEXT:\n{processed_text[:500]}...")
        print(f"{'='*90}\n")

        return processed_text

    except Exception as e:
        print(f"Error processing chunk {chunk_num}: {str(e)}")
        return chunk


def main(pdf_path: str, output_file: Optional[str] = None) -> Optional[str]:
    """Main function to process PDF content."""
    # Load environment variables
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Load configuration
    config = load_config()
    models = get_models(config)
    data_dir = get_directories(config)["data"]

    # Extract metadata
    print("Extracting metadata...")
    metadata = get_pdf_metadata(pdf_path)
    if metadata:
        print("\nPDF Metadata:")
        print(f"Number of pages: {metadata['num_pages']}")
        print("Document info:")
        for key, value in metadata["metadata"].items():
            print(f"{key}: {value}")

    # Extract text
    print("\nExtracting text...")
    extracted_text = extract_text_from_pdf(pdf_path)
    if not extracted_text:
        return None

    # Process text in chunks
    chunks = create_chunks(extracted_text, models["content_distillation"]["chunk_size"])
    processed_chunks = []

    print(f"\nProcessing {len(chunks)} chunks...")
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
        processed_chunk = process_chunk(client, chunk, i + 1, config)
        processed_chunks.append(processed_chunk)

    # Combine processed chunks
    final_text = " ".join(processed_chunks)

    # Save to file
    if output_file is None:
        output_file = os.path.join(data_dir, "processed_content.txt")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"\nProcessed content saved to: {output_file}")
    return output_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process PDF content for podcast creation"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", help="Output file path (optional)")
    args = parser.parse_args()

    main(args.pdf_path, args.output)

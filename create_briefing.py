import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from config import BRIEFING, DATA_DIR


def read_input_file(file_path: str) -> str:
    """Read content from the input file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return None


def create_briefing(content: str, output_file: str = None) -> str:
    """Create a briefing from the input content using OpenAI."""
    # Load environment variables
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        # Generate the briefing
        content = "*Only use the following content to create a briefing:* " + content
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": BRIEFING["analyst"]["system"]},
                {"role": "user", "content": content},
            ],
            temperature=0.7,
            max_tokens=5000,
        )

        briefing = response.choices[0].message.content

        # Save the briefing if output file is specified
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(briefing)
            print(f"Briefing saved to: {output_file}")

        return briefing

    except Exception as e:
        print(f"Error creating briefing: {str(e)}")
        return None


def main():
    # Define input and output paths
    input_file = os.path.join(DATA_DIR, "input", "options.txt")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(DATA_DIR, "briefings", f"briefing_{timestamp}.txt")

    # Create briefings directory if it doesn't exist
    os.makedirs(os.path.join(DATA_DIR, "briefings"), exist_ok=True)

    # Read input content
    print(f"Reading input file: {input_file}")
    content = read_input_file(input_file)
    if not content:
        print("Failed to read input file")
        return

    # Generate briefing
    print("\nGenerating briefing...")
    briefing = create_briefing(content, output_file)
    if briefing:
        print("\nBriefing generated successfully!")
        print("\nBriefing Preview:")
        print("=" * 80)
        print(briefing[:500] + "..." if len(briefing) > 500 else briefing)
        print("=" * 80)
    else:
        print("Failed to generate briefing")


if __name__ == "__main__":
    main()

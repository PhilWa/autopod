# AutoPod

An automated pipeline for generating podcast episodes from articles using AI. The pipeline fetches articles, creates LinkedIn posts, generates podcast scripts, and produces audio content using OpenAI's APIs.

## Features

- Fetches and processes recent articles
- Generates LinkedIn/X (Twitter) posts
- Creates natural conversational podcast scripts
- Generates audio using OpenAI's text-to-speech
- Combines audio segments into complete episodes

## Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment named 'lab'

## Installation

1. Create and activate the virtual environment:
   ```bash
   python -m venv lab
   source lab/bin/activate  # On Windows: lab\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage
   ```bash
    python main.py
   ```

Run the complete pipeline:

This will:
1. Fetch recent articles
2. Generate a LinkedIn post
3. Create a podcast script
4. Generate audio files
5. Combine into a final episode

## Directory Structure

- `data/` - Contains all generated content
  - `audio/` - Generated audio segments
  - `posts/` - LinkedIn posts
  - `scripts/` - Podcast scripts
  - `pod/` - Final podcast episodes

## Configuration

Adjust model parameters and speaker configurations in `config.py`.


## Example
```bash
python main.py --input-file data/input/input.txt --config-file data/config.json
```
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from get_information import setup_database
from openai import OpenAI
import os

from config_parser import (
    load_config,
    get_models,
    get_directories,
    format_linkedin_post_prompt,
)


def save_blog_post(post_content, article_ids):
    conn, cursor = setup_database()  # This will ensure the table exists

    cursor.execute(
        """
        INSERT INTO blog_posts (post_content, source_articles)
        VALUES (?, ?)
        """,
        (post_content, ",".join(map(str, article_ids))),
    )

    conn.commit()
    conn.close()


def get_latest_articles():
    conn = sqlite3.connect("content.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, date, title, content 
        FROM articles 
        ORDER BY date DESC 
        LIMIT 3
    """
    )

    articles = cursor.fetchall()
    conn.close()
    return articles


def create_linkedin_post(article_content, output_file=None, config=None):
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if config is None:
        raise ValueError("Config must be provided")

    models = get_models(config)
    directories = get_directories(config)
    post_dir = directories["posts"]

    # Prepare messages using config_parser
    messages = format_linkedin_post_prompt(config, article_content)

    response = client.chat.completions.create(
        model=models["linkedin_post"]["model"],
        messages=messages,
        temperature=models["linkedin_post"]["temperature"],
        max_tokens=models["linkedin_post"]["max_tokens"],
    )

    linkedin_post = response.choices[0].message["content"]

    # Save the post
    if output_file:
        output_path = os.path.join(post_dir, output_file)
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(post_dir, f"post_{timestamp}.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(linkedin_post)

    print(f"LinkedIn post saved to {output_path}")
    return linkedin_post


def main():
    try:
        config = load_config()
        os.makedirs(get_directories(config)["posts"], exist_ok=True)

        articles = get_latest_articles()
        if not articles:
            return

        article_ids = [article[0] for article in articles]
        article_content = [(article[1], article[2], article[3]) for article in articles]

        linkedin_post = create_linkedin_post(article_content, config=config)
        save_blog_post(linkedin_post, article_ids)

    except Exception as e:
        raise e


if __name__ == "__main__":
    main()

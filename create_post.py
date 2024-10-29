import sqlite3
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
from get_information import setup_database
from config import POST_DIR, MODELS

load_dotenv()


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


def create_linkedin_post(articles, output_file=None, models=None):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Use provided models config or fall back to default
    models = models or MODELS

    # Prepare the articles for the prompt
    articles_text = "\n\n".join(
        [
            f"Date: {article[0]}\nTitle: {article[1]}\nContent: {article[2][:500]}..."  # First 500 chars of content
            for article in articles
        ]
    )

    prompt = f"""
    ### Objective ###
    Create a LinkedIn or X (Twitter) post highlighting the top three stories of the week, including AI tech and one Swiss biotech story with a financial impact if available. The post should feel professional, engaging, and encourage readers to visit [aroundthecorner.tech](https://aroundthecorner.tech).

    ### Structure ###
    1. **Intro Sentence**: Open with “👀 Around the corner…” to introduce the stories with a unified theme.
    2. **Story Details** (repeat for each):
    - **Headline**: Catchy, non-cringy title with a relevant **emoji**
    - **Summary**: Brief 2-3 sentence overview
    - **Hashtags**: Add relevant hashtags to boost visibility
    3. **Outro**: Close with an invitation to sign up for more stories on [aroundthecorner.tech](https://aroundthecorner.tech).

    ### Requirements ###
    - **Focus** on innovation, startups, and impactful financial news in AI and Swiss biotech.
    - **Exclude** job ads and COVID-related info.
    - **Format** with short paragraphs and clear sections to enhance readability on LinkedIn and X.

    ### Only use information from the following content: ###

    {articles_text}

    """

    response = client.chat.completions.create(
        model=models["linkedin_post"]["model"],
        temperature=models["linkedin_post"]["temperature"],
        max_tokens=models["linkedin_post"]["max_tokens"],
        messages=[
            {
                "role": "system",
                "content": "You are a professional content creator specializing in switzerland-based innovation, tech, startups, and science.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    post_content = response.choices[0].message.content

    # Save the post if output_file is provided
    if output_file:
        filepath = os.path.join(POST_DIR, output_file)
    else:
        # Fallback to timestamp if no output_file provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(POST_DIR, f"linkedin_post_{timestamp}.txt")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(post_content)

    return post_content


def main():
    try:
        os.makedirs(POST_DIR, exist_ok=True)

        articles = get_latest_articles()
        if not articles:
            return

        article_ids = [article[0] for article in articles]
        article_content = [(article[1], article[2], article[3]) for article in articles]

        linkedin_post = create_linkedin_post(article_content)
        save_blog_post(linkedin_post, article_ids)

    except Exception as e:
        raise e


if __name__ == "__main__":
    main()

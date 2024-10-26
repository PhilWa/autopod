import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import sqlite3
import hashlib
import os


def setup_database():
    """Create the database and tables if they don't exist"""
    conn = sqlite3.connect(os.path.join("data", "content.db"))
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_hash TEXT UNIQUE,
            date TEXT,
            title TEXT,
            author TEXT,
            link TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_content TEXT,
            source_articles TEXT, -- Store article IDs used
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    return conn, cursor


def get_recent_articles():
    # Set up timezone for Switzerland
    zurich_tz = pytz.timezone("Europe/Zurich")
    current_date = datetime.now(zurich_tz)

    # Setup database
    conn, cursor = setup_database()

    try:
        # Send request with headers to mimic browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get("https://insideparadeplatz.ch/", headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article")

        articles_processed = 0
        articles_added = 0

        for article in articles:
            try:
                # Extract date
                date_elem = article.find("time")
                if not date_elem:
                    continue

                date_str = date_elem.text.strip()
                article_date = datetime.strptime(date_str, "%d.%m.%Y").replace(
                    tzinfo=zurich_tz
                )

                # Check if article is from last 2 days
                if current_date - article_date <= timedelta(days=2):
                    articles_processed += 1

                    # Extract title and link
                    title_elem = article.find("h2")
                    title = title_elem.text.strip()
                    link = title_elem.find("a")["href"]

                    # Extract author (if available)
                    author = article.find("span", class_="author")
                    author_text = author.text.strip() if author else ""

                    # Create unique hash for article
                    article_hash = hashlib.md5(
                        f"{date_str}{title}{link}".encode()
                    ).hexdigest()

                    # Check if article already exists
                    cursor.execute(
                        "SELECT id FROM articles WHERE article_hash = ?",
                        (article_hash,),
                    )
                    if cursor.fetchone():
                        print(f"Article already exists: {title}")
                        continue

                    # Fetch article content
                    try:
                        article_response = requests.get(link, headers=headers)
                        article_response.raise_for_status()
                        article_soup = BeautifulSoup(
                            article_response.text, "html.parser"
                        )

                        # Find the main content div
                        content = article_soup.find("div", class_="entry-content")
                        if content:
                            article_text = []
                            paragraphs = content.find_all("p")

                            for p in paragraphs:
                                if not p.find_parent(
                                    class_=["wp-caption", "social-media"]
                                ):
                                    text = p.get_text().strip()
                                    if text:
                                        article_text.append(text)

                            # Join paragraphs with single line breaks
                            full_content = "\n".join(article_text)

                            # Store in database
                            cursor.execute(
                                """
                                INSERT INTO articles (article_hash, date, title, author, link, content)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    article_hash,
                                    date_str,
                                    title,
                                    author_text,
                                    link,
                                    full_content,
                                ),
                            )

                            conn.commit()
                            articles_added += 1
                            print(f"Article saved: {title}")

                    except Exception as e:
                        print(f"Error fetching article: {title} - {str(e)}")

            except Exception as e:
                print(f"Error processing article: {str(e)}")
                continue

    except requests.RequestException as e:
        print(f"Error fetching the website: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print(f"\nProcessed {articles_processed} articles")
        print(f"Added {articles_added} new articles to database")
        conn.close()


def get_stored_articles(days=7):
    """Retrieve articles from the database"""
    conn = sqlite3.connect("inside_paradeplatz.db")
    cursor = conn.cursor()

    # Calculate date threshold
    date_threshold = (datetime.now() - timedelta(days=days)).strftime("%d.%m.%Y")

    cursor.execute(
        """
        SELECT date, title, author, link, content 
        FROM articles 
        WHERE date >= ? 
        ORDER BY date DESC
    """,
        (date_threshold,),
    )

    articles = cursor.fetchall()
    conn.close()
    return articles

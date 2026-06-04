import os
import json
import datetime
from anthropic import Anthropic
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def load_topic():
    with open("topics.json", "r") as f:
        topics = json.load(f)
    if not topics:
        raise ValueError("No topics left in topics.json!")
    return topics[0], topics[1:]


def update_topics(remaining_topics):
    with open("topics.json", "w") as f:
        json.dump(remaining_topics, f, indent=2)


def generate_article(topic):
    print(f"Generating article for topic: {topic}")
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""You are the lead writer for the blog "The Algorithmic Psyche".
Write a 900–1,200 word article on the topic: "{topic}".

Requirements:
1. Explore the intersection of artificial intelligence and psychology.
2. Make factual claims and INCLUDE citations/source links directly in the text.
3. Output the response ENTIRELY in clean, Blogger-compatible HTML (using <h2>, <p>, <ul>, <a>, etc.).
4. Do not include standard markdown formatting blocks (like ```html), output raw HTML only.
5. Do not include an <h1> as Blogger handles the title."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4000,
        system="You are an expert AI and psychology blogger.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def save_local_backup(topic, html_content):
    filename = f"{datetime.date.today()}_{topic.replace(' ', '_')[:30]}.html"
    os.makedirs("backups", exist_ok=True)
    filepath = os.path.join("backups", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Backup saved to {filepath}")


def publish_to_blogger(topic, html_content):
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get("GCP_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("GCP_CLIENT_ID"),
        client_secret=os.environ.get("GCP_CLIENT_SECRET"),
    )

    service = build("blogger", "v3", credentials=creds)
    blog_id = os.environ.get("BLOG_ID")
    is_draft = os.environ.get("PUBLISH", "false").lower() != "true"

    post_body = {
        "title": topic,
        "content": html_content,
        "labels": ["AI", "Psychology", "AEO", "AI Search", "The Algorithmic Psyche"],
    }

    response = service.posts().insert(blogId=blog_id, body=post_body, isDraft=is_draft).execute()
    status = "Published" if not is_draft else "Saved as Draft"
    print(f"Success! Post '{topic}' {status}. URL: {response.get('url', 'N/A')}")


def main():
    try:
        topic, remaining_topics = load_topic()
        html_content = generate_article(topic)
        save_local_backup(topic, html_content)
        publish_to_blogger(topic, html_content)
        update_topics(remaining_topics)
    except Exception as e:
        print(f"Error during automation: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

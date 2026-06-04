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

    prompt = f"""Write a 900–1,200 word article for Mindful Machines Journal on the topic: "{topic}".

The blog explores how AI and psychology intersect — from digital therapy and ethical design to the
future of mind-machine collaboration and mental health. Its voice is reflective, interdisciplinary,
and slightly literary: it takes ideas seriously without being academic, and it treats the reader as
someone genuinely curious about both technology and the human mind.

Requirements:
1. Ground the piece in the specific topic — don't drift into generic AI commentary.
2. Include real citations and source links inline using <a href="..."> tags.
3. Use subheadings (<h2>) to break up the piece naturally — not as a formulaic skeleton.
4. Output raw Blogger-compatible HTML only (<h2>, <p>, <ul>, <blockquote>, <a>, etc.).
5. Do not wrap output in markdown code fences. Do not include an <h1> — Blogger renders the title separately.
6. End with a short paragraph that opens a question or invites reflection — consistent with the blog's ethos."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4000,
        system=(
            "You write for Mindful Machines Journal — a blog at the intersection of AI, psychology, "
            "and mental health. Your tone is thoughtful, intellectually curious, and human. You cite "
            "real research and real events. You do not pad word counts with generic AI boosterism."
        ),
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
        "labels": ["AI and Mental Wellness", "Psychology", "Digital Therapy", "AI Ethics", "Mind-Machine Collaboration"],
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

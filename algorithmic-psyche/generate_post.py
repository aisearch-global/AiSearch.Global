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

VOICE AND STYLE — this is the most important part:
The blog's existing posts read like this: long, flowing sentences that build an idea across a
paragraph rather than firing one punchy line after another. The tone is warm and intellectually
honest — the kind of writing that treats the reader as a thoughtful friend, not a student.
It is curious rather than authoritative. It admits uncertainty. It does not lecture.

Mirror these specific qualities:
- Open with a specific observation, image, or question — never a broad generalisation like
  "In today's world, AI is changing everything." Drop the reader into a thought already in progress.
- Build ideas outward from a central question, not downward through a list of sub-points.
- Use <h2> subheadings sparingly and only where the essay genuinely shifts direction —
  not as a rigid skeleton every 200 words.
- Sentences vary: some are long and clause-heavy, some short for weight. Never a monotonous rhythm.
- Cite real research, studies, or events naturally in prose using <a href="..."> tags —
  not as a list at the end, not in brackets, not as footnotes.
- Do not use bullet points unless the content genuinely demands enumeration.
- Close with a paragraph that opens outward — a question, an unresolved tension, an invitation
  to keep thinking. Not a summary. Not "In conclusion."

CONTENT:
Ground the piece tightly in "{topic}". Do not drift into generic AI commentary.
Bring in psychology, neuroscience, philosophy of mind, or mental health research where relevant.
Aim for 900–1,200 words.

FORMAT:
Output raw Blogger-compatible HTML only: <h2>, <p>, <ul>, <blockquote>, <a>, <em>, <strong>.
No markdown. No code fences. No <h1> — Blogger renders the title separately."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        system=(
            "You are the writer behind Mindful Machines Journal — a blog exploring how AI and "
            "psychology intersect. Your voice is reflective, intellectually curious, and human. "
            "You write long-form essays, not listicles. Your sentences flow. You cite real research. "
            "You end pieces with open questions, not summaries. You never use phrases like "
            "'In today’s rapidly evolving landscape' or 'It’s clear that AI will transform.'"
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

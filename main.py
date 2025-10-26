import feedparser
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# === CONFIGURATION ===
RECIPIENT = "djvix20211@gmail.com"
EMAIL = os.getenv("EMAIL")           # Gmail address from GitHub Secrets
EMAIL_PASS = os.getenv("EMAIL_PASS") # Gmail App Password from GitHub Secrets
NUM_ARTICLES = 10

# === SOURCES ===
SOURCES = {
    "The Gradient": "https://thegradient.pub/rss/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "Papers with Code": "https://paperswithcode.com/rss",
    "Medium AI": "https://medium.com/feed/tag/artificial-intelligence",
    "Medium Computer Vision": "https://medium.com/feed/tag/computer-vision"
}

# === SIMPLE SUMMARIZER ===
def summarize_text(text, max_sentences=2):
    """
    Basic free summarizer that just extracts first few sentences.
    Keeps costs at $0 (no LLMs or APIs).
    """
    sentences = text.split('. ')
    return '. '.join(sentences[:max_sentences]) + '.' if sentences else text

# === FETCH ARTICLES ===
def fetch_articles():
    articles = []
    for name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:NUM_ARTICLES]:
                summary = summarize_text(entry.get('summary', 'No summary available.'))
                articles.append({
                    "source": name,
                    "title": entry.title,
                    "link": entry.link,
                    "summary": summary
                })
        except Exception as e:
            print(f"⚠️ Error fetching from {name}: {e}")
    return articles

# === EMAIL BUILDER ===
def build_email(articles):
    html = "<h2>🧠 AI Research & Tech Digest</h2>"
    html += f"<p>Date: {datetime.now().strftime('%Y-%m-%d')}</p>"
    html += "<hr>"
    for art in articles:
        html += f"""
        <h3>{art['title']}</h3>
        <p><b>Source:</b> {art['source']}</p>
        <p>{art['summary']}</p>
        <p><a href="{art['link']}">Read full article</a></p>
        <hr>
        """
    return html

# === SEND EMAIL ===
def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, EMAIL_PASS)
            server.send_message(msg)
            print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Error sending email:", e)

# === MAIN ===
if __name__ == "__main__":
    print("🚀 Fetching latest AI articles...")
    articles = fetch_articles()
    if not articles:
        print("⚠️ No articles found.")
    else:
        email_body = build_email(articles)
        send_email("🧠 AI Research Digest", email_body)


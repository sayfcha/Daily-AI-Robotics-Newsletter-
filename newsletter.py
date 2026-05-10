#!/usr/bin/env python3
"""
Daily AI, Robotics & Tech Newsletter
Fetches latest news from RSS feeds, compiles a digest, and sends it via email.
"""

import feedparser
import smtplib
import os
import re
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import unescape

# ── Configuration ──────────────────────────────────────────────────────────────

RECIPIENT_EMAIL = "sayfcha2@gmail.com"
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "sayfcha2@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# RSS feeds organized by category
FEEDS = {
    "🤖 Intelligence Artificielle": [
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
        ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
        ("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ],
    "🦾 Robotique": [
        ("IEEE Spectrum Robotics", "https://spectrum.ieee.org/feeds/topic/robotics.rss"),
        ("The Robot Report", "https://www.therobotreport.com/feed/"),
        ("TechCrunch Robotics", "https://techcrunch.com/category/robotics/feed/"),
    ],
    "💻 Tech & Startups": [
        ("Hacker News (top)", "https://hnrss.org/newest?points=100"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge Tech", "https://www.theverge.com/rss/tech/index.xml"),
        ("ArsTechnica", "https://feeds.arstechnica.com/arstechnica/index"),
    ],
}

MAX_ITEMS_PER_CATEGORY = 5
MAX_SUMMARY_LENGTH = 300


# ── Helpers ────────────────────────────────────────────────────────────────────

def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def truncate(text: str, max_len: int = MAX_SUMMARY_LENGTH) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


def get_entry_date(entry):
    """Extract a datetime from a feed entry."""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            from time import mktime
            return datetime.fromtimestamp(mktime(t), tz=timezone.utc)
    return None


def is_recent(entry, hours: int = 48) -> bool:
    """Check if an entry is from the last N hours (default 48 to catch weekends)."""
    dt = get_entry_date(entry)
    if dt is None:
        return True  # Include entries without dates
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return dt >= cutoff


def fetch_category(category_name: str, feeds: list) -> list:
    """Fetch and deduplicate articles for a category."""
    seen_titles = set()
    articles = []

    for source_name, url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not is_recent(entry):
                    continue

                title = strip_html(entry.get("title", "")).strip()
                if not title:
                    continue

                # Simple dedup by normalized title
                title_key = re.sub(r"[^a-z0-9]", "", title.lower())
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)

                summary = strip_html(entry.get("summary", entry.get("description", "")))
                summary = truncate(summary)

                link = entry.get("link", "")
                date = get_entry_date(entry)

                articles.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "source": source_name,
                    "date": date,
                })
        except Exception as e:
            print(f"  ⚠ Error fetching {source_name}: {e}")

    # Sort by date (most recent first), entries without dates go last
    articles.sort(key=lambda a: a["date"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return articles[:MAX_ITEMS_PER_CATEGORY]


# ── Newsletter Builder ─────────────────────────────────────────────────────────

def build_newsletter() -> tuple[str, str]:
    """Build the newsletter and return (subject, html_body)."""
    today = datetime.now().strftime("%d %B %Y")
    subject = f"🗞️ Daily AI & Robotics Briefing — {today}"

    all_sections = {}
    top_stories = []

    for category, feeds in FEEDS.items():
        print(f"📡 Fetching {category}...")
        articles = fetch_category(category, feeds)
        all_sections[category] = articles
        if articles:
            top_stories.append(articles[0])

    # Build HTML
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #1a1a1a; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 24px; }}
            .header h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
            .header p {{ margin: 0; opacity: 0.9; font-size: 14px; }}
            .top-stories {{ background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 24px; border-left: 4px solid #667eea; }}
            .top-stories h2 {{ margin-top: 0; font-size: 18px; color: #667eea; }}
            .top-stories ul {{ padding-left: 20px; }}
            .top-stories li {{ margin-bottom: 8px; }}
            .top-stories a {{ color: #1a1a1a; text-decoration: none; font-weight: 600; }}
            .top-stories a:hover {{ color: #667eea; }}
            .section {{ background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 16px; }}
            .section h2 {{ margin-top: 0; font-size: 20px; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }}
            .article {{ margin-bottom: 18px; padding-bottom: 18px; border-bottom: 1px solid #f0f0f0; }}
            .article:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
            .article h3 {{ margin: 0 0 6px 0; font-size: 16px; }}
            .article h3 a {{ color: #1a1a1a; text-decoration: none; }}
            .article h3 a:hover {{ color: #667eea; }}
            .article .meta {{ font-size: 12px; color: #888; margin-bottom: 6px; }}
            .article .summary {{ font-size: 14px; color: #444; line-height: 1.5; }}
            .footer {{ text-align: center; font-size: 12px; color: #999; margin-top: 24px; padding: 16px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🗞️ Daily AI & Robotics Briefing</h1>
            <p>{today}</p>
        </div>
    """

    # Top stories
    if top_stories:
        html += '<div class="top-stories"><h2>⚡ À retenir aujourd\'hui</h2><ul>'
        for story in top_stories:
            html += f'<li><a href="{story["link"]}">{story["title"]}</a> <span style="color:#888;font-size:12px;">— {story["source"]}</span></li>'
        html += "</ul></div>"

    # Category sections
    for category, articles in all_sections.items():
        html += f'<div class="section"><h2>{category}</h2>'
        if not articles:
            html += "<p style='color:#888;'>Rien de nouveau aujourd'hui.</p>"
        else:
            for article in articles:
                date_str = article["date"].strftime("%d/%m %H:%M") if article["date"] else ""
                html += f"""
                <div class="article">
                    <h3><a href="{article['link']}">{article['title']}</a></h3>
                    <div class="meta">{article['source']} · {date_str}</div>
                    <div class="summary">{article['summary']}</div>
                </div>
                """
        html += "</div>"

    html += """
        <div class="footer">
            <p>Généré automatiquement par ton AI Newsletter Bot 🤖</p>
            <p>Powered by GitHub Actions + Python</p>
        </div>
    </body>
    </html>
    """

    return subject, html


# ── Email Sending ──────────────────────────────────────────────────────────────

def send_email(subject: str, html_body: str):
    """Send the newsletter via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    # Plain text fallback
    text_body = f"Votre newsletter quotidienne AI & Robotics est disponible. Consultez-la dans un client email supportant le HTML."
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    print(f"📧 Sending to {RECIPIENT_EMAIL}...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("✅ Email sent!")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("🗞️ Building your daily AI & Robotics newsletter...\n")
    subject, html = build_newsletter()

    if not SENDER_PASSWORD:
        print("⚠ No SENDER_PASSWORD set. Saving newsletter to file instead.")
        filename = f"newsletter_{datetime.now().strftime('%Y-%m-%d')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📄 Saved to {filename}")
        return

    send_email(subject, html)


if __name__ == "__main__":
    main()

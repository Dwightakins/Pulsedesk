# PulseDesk

**Stop scrolling through news sites every morning. PulseDesk delivers your personalized business intelligence digest before your first cup of coffee, and again before you leave the office.**

An AI-powered news agent. The AI goes through the web, scrapes the latest Nigerian tech, business, finance, and entertainment news, summarizes it, and sends it to your inbox twice a day.

Built by [Dwight Akinyanju](https://github.com/Dwightakins)

---

## The Problem

Founders and executives waste 30-45 minutes every morning scanning multiple news sources to stay informed. Most of what they read is noise. The signal gets buried.

## The Solution

PulseDesk runs automatically at 7am and 6pm, goes through the web for the latest Nigerian news, uses AI to extract only what matters, scores each story by relevance, and delivers a clean branded email digest. Zero effort from the reader.

---

## How It Works

    Scrape (AI goes through the web for the latest news)
         |
    Summarize (AI, relevance scoring 0-1)
         |
    Filter (only 60%+ relevance makes the cut)
         |
    Format (branded HTML email with Morning/Evening editions)
         |
    Deliver (Gmail SMTP, twice daily)

**The entire pipeline runs in about a minute.**

---

## What It Covers

| Category | Coverage |
|----------|----------|
| Tech | Startups, funding, product launches, digital economy |
| Business | Economy, policy, market updates, industry reports |
| Finance | Stocks, bonds, economic analysis, investment |
| Entertainment | Lifestyle, culture, celebrity news |

Coverage is configurable in the scraper config.

---

## Architecture

| File | What It Does |
|------|-------------|
| `scrapers.py` | Concurrent web scraping with retry logic, timeout handling, fallback extraction, and URL normalization |
| `summarizer.py` | AI integration for article summarization and relevance scoring |
| `email_sender.py` | HTML email builder with branded Morning/Evening templates and SMTP delivery |
| `main.py` | Pipeline orchestrator with CLI interface and twice-daily scheduler |

---

## Quick Start

**1. Clone and install**

    git clone https://github.com/Dwightakins/Pulsedesk.git
    cd Pulsedesk
    pip install -r requirements.txt

**2. Configure environment**

Create a `.env` file in the project root:

    GMAIL_USER=your_gmail@gmail.com
    GMAIL_PASSWORD=your_gmail_app_password
    RECIPIENT_EMAIL=recipient@gmail.com
    GROQ_API_KEY=your_groq_api_key

Gmail App Password: myaccount.google.com > Security > App passwords

AI provider key: PulseDesk currently uses Groq (console.groq.com). The provider can be swapped in `summarizer.py`.

**3. Send your first digest**

    python main.py --now

**4. Schedule twice-daily delivery**

    python main.py --schedule

---

## Usage

    python main.py --now                    Send Morning digest now
    python main.py --now Evening            Send Evening digest now
    python main.py --schedule               Schedule at 07:00 and 18:00
    python main.py --schedule 06:00 19:00   Custom morning and evening times
    python main.py --help                   Show help

---

## Tech Stack

- **Python 3.14.5** with concurrent futures for parallel scraping
- **BeautifulSoup4** for HTML parsing and article extraction
- **AI model API** for intelligent summarization and relevance scoring
- **SMTP** for email delivery via Gmail
- **Schedule** for automated twice-daily execution

---

## What Makes This Different

Most newsletter tools require manual curation. PulseDesk is fully autonomous. Set it once, and it delivers value every morning and evening without intervention. The AI does not just summarize. It scores relevance so the reader sees the most important stories first.

---

## Roadmap

- [ ] Web-based signup page for subscribers
- [ ] Admin dashboard for source and subscriber management
- [ ] n8n/Make.com integration for visual workflow automation
- [ ] Multi-subscriber support with personalized topic preferences
- [ ] Weekly deep-dive research edition (premium tier)

---

## License

MIT

---

Built with purpose.

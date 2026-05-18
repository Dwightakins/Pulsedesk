# PulseDesk

**Stop checking 12 websites every morning. PulseDesk delivers your personalized business intelligence digest before your first cup of coffee.**

An AI-powered news agent that scrapes, summarizes, and delivers curated intelligence from Nigerian business, African tech, and global art markets directly to your inbox every day.

Built by [Dwight Akinyanju](https://github.com/Dwightakins)

---

## The Problem

Founders and executives waste 30-45 minutes every morning scanning multiple news sources to stay informed. Most of what they read is noise. The signal gets buried.

## The Solution

PulseDesk runs automatically at 7am, pulls the latest from 5+ curated sources, uses Mistral AI to extract only what matters, scores each story by relevance, and delivers a clean branded email digest. Zero effort from the reader.

---

## How It Works

    Scrape (5 sources, concurrent)
         |
    Summarize (Mistral AI, relevance scoring 0-1)
         |
    Filter (only 60%+ relevance makes the cut)
         |
    Format (branded HTML email template)
         |
    Deliver (Gmail SMTP, 7am daily)

**The entire pipeline runs in under 30 seconds.**

---

## Sources

| Category | Source | Coverage |
|----------|--------|----------|
| Business | Nairametrics | Nigerian finance, bonds, markets |
| Business | BusinessDay Nigeria | Economy, policy, regulation |
| Tech | TechPoint Africa | African startups, funding, product launches |
| Art | Artnews | Global art market, auctions, galleries |
| Art | Art Africa Magazine | African art, exhibitions, interviews |

Sources are configurable. Add or remove any site by editing the scraper config.

---

## Architecture

| File | What It Does |
|------|-------------|
| `scrapers.py` | Concurrent web scraping with retry logic, timeout handling, and URL normalization |
| `summarizer.py` | Mistral AI integration for article summarization and relevance scoring |
| `email_sender.py` | HTML email builder with branded template and SMTP delivery |
| `main.py` | Pipeline orchestrator with CLI interface and daily scheduler |

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
    MISTRAL_API_KEY=your_mistral_api_key

Gmail App Password: myaccount.google.com > Security > App passwords

Mistral API Key: console.mistral.ai

**3. Send your first digest**

    python main.py --now

**4. Schedule daily delivery**

    python main.py --schedule 07:00

---

## Usage

    python main.py --now              Send digest immediately
    python main.py --schedule         Schedule daily at 07:00
    python main.py --schedule 09:00   Schedule at custom time
    python main.py --help             Show help

---

## Tech Stack

- **Python 3.10+** with concurrent futures for parallel scraping
- **BeautifulSoup4** for HTML parsing and article extraction
- **Mistral AI API** for intelligent summarization and relevance scoring
- **SMTP** for email delivery via Gmail
- **Schedule** for automated daily execution

---

## What Makes This Different

Most newsletter tools require manual curation. PulseDesk is fully autonomous. Set it once, and it delivers value every morning without intervention. The AI doesn't just summarize, it scores relevance so the reader sees the most important stories first.

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

Built with purpose in Lagos, Nigeria.

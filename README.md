# PulseDesk

**Stop checking 12 websites every morning. PulseDesk delivers your personalized business intelligence digest before your first cup of coffee, and again before you leave the office.**

An AI-powered news agent that scrapes, summarizes, and delivers curated intelligence from Nigerian tech, business, finance, and entertainment sources directly to your inbox twice a day.

Built by [Dwight Akinyanju](https://github.com/Dwightakins)

---

## The Problem

Founders and executives waste 30-45 minutes every morning scanning multiple news sources to stay informed. Most of what they read is noise. The signal gets buried.

## The Solution

PulseDesk runs automatically at 7am and 6pm, pulls the latest from curated Nigerian sources, uses Mistral AI to extract only what matters, scores each story by relevance, and delivers a clean branded email digest. Zero effort from the reader.

---

## How It Works

    Scrape (11 sources, concurrent)
         |
    Summarize (Mistral AI, relevance scoring 0-1)
         |
    Filter (only 60%+ relevance makes the cut)
         |
    Format (branded HTML email with Morning/Evening editions)
         |
    Deliver (Gmail SMTP, twice daily)

**The entire pipeline runs in under 40 seconds.**

---

## Sources

| Category | Source | Coverage |
|----------|--------|----------|
| Tech | TechCabal | African tech ecosystem, startups, funding |
| Tech | TechPoint Africa | African tech news, product launches |
| Tech | TechNext | Nigerian tech innovation, digital economy |
| Business | BusinessDay Nigeria | Nigerian economy, policy, regulation |
| Business | The Guardian Nigeria | Nigerian business news, market updates |
| Business | Punch Newspapers | Nigerian business, industry reports |
| Finance | Nairametrics | Nigerian finance, bonds, stock market |
| Finance | TheCable Business | Nigerian economic analysis, policy impact |
| Finance | Premium Times Business | Nigerian business investigations, finance |
| Entertainment | BellaNaija | Nigerian lifestyle, entertainment, culture |
| Entertainment | Pulse Nigeria | Nigerian entertainment, celebrity news |

Sources are configurable. Add or remove any site by editing the scraper config.

---

## Architecture

| File | What It Does |
|------|-------------|
| `scrapers.py` | Concurrent web scraping with retry logic, timeout handling, fallback extraction, and URL normalization |
| `summarizer.py` | Mistral AI integration for article summarization and relevance scoring |
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
    MISTRAL_API_KEY=your_mistral_api_key

Gmail App Password: myaccount.google.com > Security > App passwords

Mistral API Key: console.mistral.ai

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
- **Mistral AI API** for intelligent summarization and relevance scoring
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

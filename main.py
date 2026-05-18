import schedule
import time
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pulsedesk.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('pulsedesk')

from scrapers import ArticleAggregator
from summarizer import ArticleSummarizer
from email_sender import DigestEmailBuilder, DigestSender


class PulseDesk:
    def __init__(self):
        self.aggregator = ArticleAggregator()
        self.summarizer = ArticleSummarizer()
        self.email_builder = DigestEmailBuilder()
        self.email_sender = DigestSender()
        self.run_count = 0
    
    def run_digest(self, edition: str = "Morning"):
        """Execute the full digest pipeline"""
        self.run_count += 1
        start_time = datetime.now()
        
        logger.info(f"{'='*60}")
        logger.info(f"PULSEDESK {edition.upper()} EDITION - Run #{self.run_count}")
        logger.info(f"{'='*60}")
        
        try:
            # Step 1: Scrape
            logger.info("STEP 1: Scraping sources...")
            articles = self.aggregator.get_articles()
            logger.info(f"Scraped {len(articles)} articles")
            
            if not articles:
                logger.warning("No articles scraped. Skipping digest.")
                return False
            
            # Step 2: Summarize
            logger.info("STEP 2: Summarizing with Mistral AI...")
            summaries = self.summarizer.summarize_batch(articles)
            filtered = self.summarizer.filter_by_relevance(summaries, threshold=0.6)
            sorted_summaries = self.summarizer.sort_by_relevance(filtered)
            logger.info(f"Generated {len(sorted_summaries)} relevant summaries")
            
            if not sorted_summaries:
                logger.warning("No relevant summaries generated. Skipping digest.")
                return False
            
            # Step 3: Build and send
            logger.info("STEP 3: Building and sending digest...")
            message = self.email_builder.build_digest(sorted_summaries[:12], edition=edition)
            success = self.email_sender.send(message)
            
            elapsed = (datetime.now() - start_time).seconds
            
            if success:
                logger.info(f"{edition} digest delivered in {elapsed}s | {len(articles)} scraped | {len(sorted_summaries)} summarized")
                return True
            else:
                logger.error(f"{edition} digest failed after {elapsed}s")
                return False
        
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_morning(self):
        """Morning edition"""
        self.run_digest(edition="Morning")
    
    def run_evening(self):
        """Evening edition"""
        self.run_digest(edition="Evening")
    
    def start_scheduler(self, morning_time: str = "07:00", evening_time: str = "18:00"):
        """Schedule twice-daily digest"""
        schedule.every().day.at(morning_time).do(self.run_morning)
        schedule.every().day.at(evening_time).do(self.run_evening)
        
        logger.info(f"PulseDesk scheduler started")
        logger.info(f"Morning digest: {morning_time}")
        logger.info(f"Evening digest: {evening_time}")
        logger.info(f"Recipient: {os.getenv('RECIPIENT_EMAIL')}")
        logger.info(f"Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                next_run = schedule.next_run()
                if next_run:
                    time_left = next_run - datetime.now()
                    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    sys.stdout.write(f"\rNext digest in: {hours:02d}h {minutes:02d}m {seconds:02d}s")
                    sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")


def main():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║              PULSEDESK v1.0                   ║
    ║     AI-Powered Daily Intelligence Digest      ║
    ║        Morning & Evening Editions             ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    pulse = PulseDesk()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--now":
            edition = sys.argv[2] if len(sys.argv) > 2 else "Morning"
            print(f"Running {edition} digest immediately...\n")
            pulse.run_digest(edition=edition)
        
        elif sys.argv[1] == "--schedule":
            morning = sys.argv[2] if len(sys.argv) > 2 else "07:00"
            evening = sys.argv[3] if len(sys.argv) > 3 else "18:00"
            pulse.start_scheduler(morning, evening)
        
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  py main.py --now                    Run Morning digest now")
            print("  py main.py --now Evening             Run Evening digest now")
            print("  py main.py --schedule                Schedule at 07:00 & 18:00")
            print("  py main.py --schedule 06:00 19:00    Custom morning & evening times")
            print("  py main.py --help                    Show this help")
    else:
        print("What would you like to do?\n")
        print("  1. Send Morning digest now")
        print("  2. Send Evening digest now")
        print("  3. Schedule twice daily (7:00 AM & 6:00 PM)")
        print("  4. Schedule at custom times")
        print("")
        
        choice = input("Enter choice (1/2/3/4): ").strip()
        
        if choice == "1":
            pulse.run_digest(edition="Morning")
        elif choice == "2":
            pulse.run_digest(edition="Evening")
        elif choice == "3":
            pulse.start_scheduler("07:00", "18:00")
        elif choice == "4":
            morning = input("Morning time (HH:MM, 24hr): ").strip()
            evening = input("Evening time (HH:MM, 24hr): ").strip()
            pulse.start_scheduler(morning, evening)
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()

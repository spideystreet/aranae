
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler(verbose=True, user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36") as crawler:
        result = await crawler.arun(url="https://www.free-work.com/fr/tech-it/jobs")
        
        html = result.html
        print(f"\n--- HTML Length: {len(html)} ---\n")
        
        if "fw-text-highlight" in html:
             count = html.count("fw-text-highlight")
             print(f"Found 'fw-text-highlight' {count} times.")
        else:
             print("WARNING: 'fw-text-highlight' NOT found in HTML.")

        # Check for specific job title known from previous dumps
        if "Specialiste Workplace" in html:
             print("Found 'Specialiste Workplace' job.")

if __name__ == "__main__":
    asyncio.run(main())

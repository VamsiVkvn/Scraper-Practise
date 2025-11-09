import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://quotes.toscrape.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; practice-scraper/1.0; +https://example.com/bot)"}

def create_session(retries=3, backoff=0.5):
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff,
                  status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update(HEADERS)
    return s

session = create_session()

def get_soup(url):
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")

def parse_quote_block(quote):
    text = quote.find("span", class_="text").get_text(strip=True)
    author = quote.find("small", class_="author").get_text(strip=True)
    tags = [t.get_text(strip=True) for t in quote.select(".tags a.tag")]
    link = quote.find("a", href=True)
    author_url = urljoin(BASE_URL, link["href"]) if link else None
    return {"text": text, "author": author, "tags": tags, "author_url": author_url}

def scrape_quotes(pages_to_scrape=3):
    results = []
    url = BASE_URL
    for page in range(pages_to_scrape):
        print(f"[INFO] Scraping page {page+1}...")
        soup = get_soup(url)
        for q in soup.select("div.quote"):
            results.append(parse_quote_block(q))
        next_btn = soup.select_one("li.next a")
        if not next_btn:
            break
        url = urljoin(BASE_URL, next_btn["href"])
        time.sleep(random.uniform(1, 2))
    return results

def save_to_csv(data, filename="quotes_sample.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags", "author_url"])
        writer.writeheader()
        for row in data:
            row["tags"] = "; ".join(row["tags"])
            writer.writerow(row)
    print(f"[INFO] Saved {len(data)} quotes to {filename}")

if __name__ == "__main__":
    quotes = scrape_quotes()
    save_to_csv(quotes)

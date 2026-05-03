import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import argparse

parser = argparse.ArgumentParser(description="Web Crawler")
parser.add_argument("-u", "--url", required=True, help="Starting URL")
parser.add_argument("-m", "--max-pages", type=int, default=50, help="Max pages to crawl")
parser.add_argument("-d", "--depth", type=int, default=3, help="Max depth")

args = parser.parse_args()

# Access values like:
print(args.url)
print(args.max_pages)

def crawl(start_url, max_page=50):
    visited = set()
    queue = deque([start_url])
    base_domain = urlparse(start_url).netloc

    while queue and len(visited) < max_page:
        url = queue.popleft()

        if url in visited:
            continue
        try: 
            response = requests.get(url, timeout=5)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue
            visited.add(url)
            print(f"[{len(visited)}] Crawled : {url}")

            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup.find_all("a", href=True):
                link = urljoin(url, tag["href"])

                if urlparse(link).netloc == base_domain and link not in visited:
                    queue.append(link)
        except Exception as e:
            print(f"Error Crawling {url}: {e}")
    return visited


crawl(args.url, args.max_pages)



link = urljoin(args.url, tag["href"])
print(link)
import requests
import sys
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import argparse
import urllib.robotparser

# set up arguments
parser = argparse.ArgumentParser(description="Web Crawler")
parser.add_argument("-u", "--url", required=True, help="Starting URL")
parser.add_argument("-m", "--max-pages", type=int, default=50, help="Max pages to crawl")
parser.add_argument("-d", "--depth", type=int, default=3, help="Max depth")

args = parser.parse_args()

USER_AGENT = "MyCrawler/1.0"


# define crawler
def crawl(start_url, max_page=50):
    visited = set() # track visited URLs
    queue = deque([start_url]) # queue of URLs to visit

    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc # extract domain
    robots_txt_url = f"{parsed_start.scheme}://{base_domain}/robots.txt"

    # setup for robots.txt
    robot_parser = urllib.robotparser.RobotFileParser()
    robot_parser.set_url(robots_txt_url)

    try:
        robot_parser.read()
        crawl_delay = (
            robot_parser.crawl_delay(USER_AGENT) or robot_parser.crawl_delay("*") or 1
        )
        print(f"robots.txt loaded. Crawl delay: {crawl_delay}s")
    except Exception as e:
        print(f"Could not read robots.txt ({e}). proceeding with default delay.")
        robot_parser = None
        crawl_delay = 1

    # keep crawling until queue is empty and we hit the page limit
    while queue and len(visited) < max_page:
        url = queue.popleft()

        if url in visited: # skip if URL already visited
            continue

        if robot_parser and not robot_parser.can_fetch(USER_AGENT, url):
            print(f"Blocked by robots.txt: {url}")
            continue

        time.sleep(crawl_delay)

        
        try: 
            response = requests.get(url, timeout=5, headers={"User-Agent": USER_AGENT}) # fetch the page, give up after 5 sec
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue
            visited.add(url) # mark this URL as visited 
            print(f"[{len(visited)}] Crawled : {url}")

            soup = BeautifulSoup(response.text, "html.parser") # parse the HTML content of the page

            # find all hyperlinks on the page
            for tag in soup.find_all("a", href=True):
                link = urljoin(url, tag["href"]) # convert relateive URL to absolute

                # only add the link if it is on the same domain and not visited yet
                if urlparse(link).netloc == base_domain and link not in visited:
                    queue.append(link)
        except Exception as e:
            print(f"Error Crawling {url}: {e}") # print any error occurred
    return visited


crawl(args.url, args.max_pages)

""" command to execute : python3 web_crawler.py -u https://target.com  
                            OR 
 python3 web_crawler.py -u https://target.com -m <page_limit> (optional) """





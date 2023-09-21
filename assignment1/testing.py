import requests
from bs4 import BeautifulSoup
import heapq
import random
import time

# Define the initial search query
initial_query = input("Enter the search query: ")

# Initialize data structures for crawling
crawl_queue = []  # Priority queue for URLs to crawl
visited_urls = set()  # Set to keep track of visited URLs
sampled_urls = []  # List to store sampled URLs
max_pages_to_crawl = 100  # Maximum number of pages to crawl
max_images_threshold = 10  # Threshold for the number of images on a page

# Define a function to fetch and parse a webpage
def fetch_and_parse(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
    return None


# Define a function to extract hyperlinks from a webpage
def extract_links(soup):
    links = []
    if soup:
        for link in soup.find_all("a", href=True):
            links.append(link["href"])
    return links


# Seed the crawl queue with search engine results
search_url = f"https://www.example.com/search?q={initial_query}"
search_results = fetch_and_parse(search_url)

if search_results:
    links = extract_links(search_results)[:10]  # Get the top 10 results
    for link in links:
        heapq.heappush(crawl_queue, link)

# Define the random walk strategy
def random_walk_strategy():
    while crawl_queue and len(sampled_urls) < max_pages_to_crawl:
        url = heapq.heappop(crawl_queue)
        if url not in visited_urls:
            visited_urls.add(url)
            page = fetch_and_parse(url)
            if page:
                num_images = len(page.find_all("img"))
                sampled = num_images <= max_images_threshold
                sampled_urls.append((url, num_images, sampled, time.time()))
                links = extract_links(page)
                random.shuffle(links)
                for link in links:
                    if link not in visited_urls:
                        heapq.heappush(crawl_queue, link)


# Start crawling using the random walk strategy
random_walk_strategy()

# Write the log file
log_file = "crawler_log.txt"
with open(log_file, "w") as f:
    for url, num_images, sampled, timestamp in sampled_urls:
        sampled_str = "Sampled" if sampled else "Traversed"
        f.write(f"{timestamp} - {sampled_str}: {url} (Images: {num_images})\n")

print(f"Crawling completed. Log file saved as {log_file}")

import requests
from bs4 import BeautifulSoup
import collections
import random
import time
from googlesearch import search
import tldextract

# Define the initial search query
# initial_query = input("Enter the search query: ")

# Initialize data structures for crawling
crawl_queue = collections.deque()  # Priority queue for URLs to crawl
visited_urls = set()  # Set to keep track of visited URLs
sampled_urls = []  # List to store sampled URLs
# max_pages_to_crawl = 100  # Maximum number of pages to crawl
# max_images_threshold = 10  # Threshold for the number of images on a page

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
# search_url = f"https://www.example.com/search?q={initial_query}"
# search_results = fetch_and_parse(search_url)

# if search_results:
#     links = extract_links(search_results)[:10]  # Get the top 10 results
#     for link in links:
#         heapq.heappush(crawl_queue, link)


# check the domain


def check_domain(url1, url2):
    domain_name_of_url1 = tldextract.extract(url1).domain
    domain_name_of_url2 = tldextract.extract(url2).domain
    if domain_name_of_url1 != domain_name_of_url2:
        return True
    else:
        return False


# Define the random walk strategy
def random_walk_strategy():
    while crawl_queue and len(sampled_urls) < 100:

        url = crawl_queue[0]
        crawl_queue.popleft()
        if url not in visited_urls:
            visited_urls.add(url)
            page = fetch_and_parse(url)
            if page:
                num_images = len(page.find_all("img"))
                # sampled = num_images <= max_images_threshold
                sampled_urls.append((url, num_images, time.time()))
                links = extract_links(page)
                random.shuffle(links)
                for link in links:
                    if link not in visited_urls and check_domain(link, url):
                        crawl_queue.appendleft(link)
                    else:
                        crawl_queue.append(link)


# Start crawling using the random walk strategy
# random_walk_strategy()

# Write the log file
log_file = "crawler_log.txt"
with open(log_file, "w") as f:
    for url, num_images, sampled, timestamp in sampled_urls:
        print(url)
        print(timestamp)
        sampled_str = "Sampled" if sampled else "Traversed"
        f.write(f"{timestamp} - {sampled_str}: {url} (Images: {num_images})\n")

print(f"Crawling completed. Log file saved as {log_file}")

if __name__ == "__main__":
    # seed_urls = []
    # max_pages = 50

    user_query = input("Enter your search query: ")
    top_results = list(search(user_query, num=10, stop=10))
    response = f"Top 10 results for '{user_query}':\n"
    for idx, result in enumerate(top_results, start=1):
        response += f"{idx}. {result}\n"
        crawl_queue.appendleft(result)

        # seed_urls.append(result)

    # print(response)
    # web_crawler(seed_urls, 100)
    random_walk_strategy()

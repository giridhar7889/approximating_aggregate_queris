import requests
from bs4 import BeautifulSoup
import queue
import re
import time
import random
import urllib.robotparser
from urllib.parse import urlparse
import tldextract
from googlesearch import search
import collections

# # urls = queue.PriorityQueue()
# # urls.put(("https://github.com/orgs/python/repositories?type=all", 0.5))
# def crawler_fun(urls):
#     # print(urls)

#     visited_urls = set()

#     while not urls.empty() and len(visited_urls) < 50:
#         print("inside")

#         current_url, _ = urls.get()
#         print(current_url)
#         visited_urls.add(current_url)
#         domain_name = tldextract.extract(current_url).domain
#         print(domain_name)
#         # checks if url is valid
#         result = urlparse(current_url)
#         if not (result.scheme and result.netloc):
#             print("url is invalid")
#             continue
#         # does DNS lookup for name resolution
#         # fetches the page from the server
#         response = requests.get(current_url)
#         soup = BeautifulSoup(response.content, "html.parser")
#         visited_urls.add(current_url)
#         # fetches robots.txt from site unless robots file cached
#         rp = urllib.robotparser.RobotFileParser()
#         rp.set_url(current_url + "/robots.txt")
#         rp.read()
#         link_elements = soup.select("a[href]")
#         # parse the page to find new hyperlinks
#         for link_element in link_elements:
#             url = link_element["href"]
#             subdomain_name = tldextract.extract(url).domain
#             print("inside subdomain")
#             print(subdomain_name)
#             # check if the url is relative to the domain or any of its subdomian
#             if subdomain_name == domain_name:
#                 # check if the useragent is allowed to fetch the url according
#                 # to the rules contained in the parsed robots.txt file.
#                 if rp.can_fetch("*", url):
#                     # check if the url discovered is new
#                     if url not in visited_urls and url not in [
#                         item[0] for item in urls.queue
#                     ]:
#                         # assign priority
#                         p_s = 1
#                         # check if its a pagination page
#                         # if re.match(
#                         #     r"^https://github.com/orgs/python/repositories?page=\d+/?$&type=all",
#                         #     url,
#                         # ):
#                         # p_s = 0.5
#                         urls.put((url, p_s))

#                 else:
#                     print("cant fetch")
#         # pause the script for a random delay
#         time.sleep(random.uniform(1, 3))

import requests
from bs4 import BeautifulSoup
import queue

# Initialize a queue to hold URLs to be crawled
# urls = queue.PriorityQueue()
crawl_queue = collections.deque()
sampled_urls = []

# Function to fetch and parse a web page
def fetch_and_parse(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching {url}: {str(e)}")
        return None


# Function to extract and add new links to the crawl queue
def extract_links(soup):
    links = []
    for a_tag in soup.find_all("a", href=True):
        link = a_tag["href"]
        # Ensure that the link is an absolute URL
        # you can check if the url is valid or not
        if link.startswith("http") or link.startswith("https"):
            links.append(link)
    return links


def check_domain(url1, url2, visited_set):
    domain_name_of_url1 = tldextract.extract(url1).domain
    domain_name_of_url2 = tldextract.extract(url2).domain

    # print("1" + domain_name_of_url1)
    # print("2" + domain_name_of_url2)
    if domain_name_of_url1 != domain_name_of_url2:
        list_of_visited_domains = []
        for link in visited_set:
            list_of_visited_domains.append(tldextract.extract(link).domain)
        if domain_name_of_url1 not in list_of_visited_domains:
            return True
    else:
        return False


# Function to crawl the web
def web_crawler(seed_urls, max_pages):
    visited = set()
    for seed_url in seed_urls:
        crawl_queue.append(seed_url)

    while len(crawl_queue) > 0 and len(sampled_urls) < max_pages:
        current_url = crawl_queue[0]
        crawl_queue.popleft()
        if current_url not in visited:
            print(f"Crawling: {current_url}")
            soup = fetch_and_parse(current_url)
            if soup and check_rp(current_url):
                num_images = len(soup.find_all("img"))
                sampled = num_images <= 100
                sampled_urls.append((current_url, num_images, sampled, time.time()))
                links = extract_links(soup)
                random.shuffle(links)
                # soup html page and it has elements
                visited.add(current_url)
                # new_links = extract_links(soup)
                for link in links:
                    if link not in visited and check_domain(link, current_url, visited):
                        crawl_queue.appendleft(link)
                    else:
                        crawl_queue.append(link)

    log_file = "crawler_log_first.txt"
    with open(log_file, "w") as f:
        for url, num_images, sampled, timestamp in sampled_urls:
            print(url)
            print(timestamp)
            sampled_str = "Sampled" if sampled else "Traversed"
            f.write(f"{timestamp} - {sampled_str}: {url} (Images: {num_images})\n")

    # for url, num_images, sampled, timestamp in sampled_urls:
    #     sampled_str = "Sampled" if sampled else "Traversed"
    #     print(f"{timestamp} - {sampled_str}: {url} (Images: {num_images})\n")


def check_rp(crawling_url):
    # fetches robots.txt from site unless robots file cached
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(crawling_url + "/robots.txt")
    rp.read()
    # check if the useragent is allowed to fetch the url according
    # to the rules contained in the parsed robots.txt file.
    if rp.can_fetch("*", crawling_url):
        return True
    else:
        return False


# Example usage
if __name__ == "__main__":
    seed_urls = []
    # max_pages = 50

    user_query = input("Enter your search query: ")
    top_results = list(search(user_query, num=10, stop=10))
    response = f"Top 10 results for '{user_query}':\n"
    for idx, result in enumerate(top_results, start=1):
        response += f"{idx}. {result}\n"
        seed_urls.append(result)

    print(response)
    web_crawler(seed_urls, 100)

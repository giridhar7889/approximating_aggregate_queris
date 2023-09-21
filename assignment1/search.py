from crawler import *
from googlesearch import search
import queue

urls = queue.Queue()


def google_search(user_query):
    top_results = list(search(user_query, num=10, stop=10))
    response = f"Top 10 results for '{user_query}':\n"
    for idx, result in enumerate(top_results, start=1):
        response += f"{idx}. {result}\n"
        urls.put((result))

    print(response)
    web_crawler(urls, 100)


user_query = input("Enter your search query: ")
google_search(user_query)

# try:
#     from googlesearch import search
# except ImportError:
#     print("No module named 'google' found")

# # to search
# query = "python "

# for j in search(query, num=10, stop=10, pause=2):
#     print(j)

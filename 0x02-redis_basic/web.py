#!/usr/bin/env python3
"""A module with tools for request caching and tracking
"""
import requests
import redis
import time

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
def get_page(url: str) -> str:
    """ Check if the URL result is already cached"""
    cached_content = redis_client.get(f'cache:{url}')
    if cached_content:
        print("Cached result found.")
        return cached_content.decode('utf-8')
    """ If not cached, fetch the HTML content"""
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        """ Cache the content with a 10-second expiration"""
        redis_client.setex(f'cache:{url}', 10, content)
        return content
    return "Error: Unable to fetch the page."

""" Define a decorator to track the number of times a URL is accessed"""
def track_url_access(func):
    def wrapper(url):
       """Increment the access count"""
        count_key = f'count:{url}'
        current_count = redis_client.incr(count_key)

        """ Set an expiration for the count key to 10 seconds"""
        if current_count == 1:
            redis_client.expire(count_key, 10)

       """ Call the original function and return the result"""
        result = func(url)
        return result
    return wrapper
""" Apply the decorator to the get_page function"""
get_page = track_url_access(get_page)

""" Example usage"""
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/https://example.com"
    content = get_page(url)
    print(content)

import re

import requests
from bs4 import BeautifulSoup


class SitemapParser:
    @staticmethod
    def read_robots(domain):
        res = requests.get(f"https://www.{domain}/robots.txt").text
        res = [
            re.sub(".+(?<=:\s)", "", line)
            for line in res.split("\n") 
            if "Sitemap" in line
        ]

        return res

    @staticmethod
    def read_sitemap_index(url):
        res = requests.get(url)
        if res.ok and "urlset" in res.text:
            return [url]

        if not (res.ok and "sitemapindex" in res.text):
            raise ValueError("Invalid Sitemap Index")
        
        res = BeautifulSoup(res.text, features="lxml")
        res = [loc.text for loc in res.find_all("loc")]

        return res

    @staticmethod
    def read_urlset(url):
        res = requests.get(url)
        if not (res.ok and "urlset" in res.text):
            raise ValueError("Invalid Sitemap")

        res = BeautifulSoup(res.text)
        res = [loc.text for loc in res.find_all("loc")]
        return res
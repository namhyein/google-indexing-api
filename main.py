import time
import argparse

from package import BingIndexnow
from package import GoogleSearchConsole
from package import SitemapParser

parser = argparse.ArgumentParser(prog='VeenoverseURLInspection')

parser.add_argument("-a", "--auth", help="Google Refresh Token / Bing API Credentials", required=True)
parser.add_argument("-d", "--domain", help="Domain Name you want to index (format: domain.com)", required=True)
parser.add_argument("-c", "--console", help="One of [bing, google]", default="google")

parser.add_argument("--sitemap", help="Sitemap URL", default=None)


def execute_google(domain, credentials, sitemaps=None):
    gsc = GoogleSearchConsole(args.domain, args.auth)
    if not sitemaps:
        sitemaps = SitemapParser.read_robots(domain)

    for sitemap in sitemaps:
        urlsets = SitemapParser.read_sitemap_index(sitemap)
        for urlset in urlsets:
            urls = SitemapParser.read_urlset(urlset)
            for url in urls:
                status_code = gsc.url_inspection(url)
                if status_code == 429:
                    return gsc.execute()
    return gsc.execute()

def execute_bing(domain, credentials, option, sitemaps=None):
    bing = BingIndexnow(domain, credentials)
    if not sitemaps:
        sitemaps = SitemapParser.read_robots(domain)

    for sitemap in sitemaps:
        urlsets = SitemapParser.read_sitemap_index(sitemap)
        for urlset in urlsets:
            urls = SitemapParser.read_urlset(urlset)
            for url in urls:
                status_code = bing.url_inspection(url)
                if status_code == 429:
                    return

    return bing.execute()

if __name__ == "__main__":
    args = parser.parse_args()

    main = locals()[f"execute_{args.console}"]

    main(args.domain, args.auth, [args.sitemap] if args.sitemap else None)
    print("DONE")


#!/usr/bin/env python3
"""
Usage: linkrot.py urls.txt items.jl
"""
import time
import argparse

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.url import add_http_if_no_scheme
from scrapy.http.response import Response
try:
    import soft404
except ImportError:
    soft404 = None


def read_urls(fp):
    """ Read a file with urls, one url per line. """
    for line in fp:
        url = line.strip()
        if not url:
            continue
        if url == 'url':
            continue  # optional header
        yield add_http_if_no_scheme(url)


class LinkrotSpider(scrapy.Spider):
    name = 'linkrot'
    urls = None  # path to a file with urls to monitor
    handle_httpstatus_list = list(range(200, 300)) + list(range(400, 600))

    def start_requests(self):
        start_time = time.time()
        with open(self.urls, 'rt') as f:
            for url in read_urls(f):
                yield scrapy.Request(url, self.parse,
                    errback=self.parse_error,
                    meta={'url': url, 'start': start_time},
                )

    def parse(self, response: Response):
        item = {
            'url': response.meta['url'],
            'crawl': response.meta['start'],
            'crawled_url': response.url,
            'status_code': response.status,
            'size': len(response.body),
            'crawled_at': time.time(),
        }
        if soft404 is not None:
            item['soft404'] = soft404.probability(response.text)
        yield item

    def parse_error(self, failure):
        request = failure.request
        yield {
            'url': request.meta['url'],
            'crawl': request.meta['start'],
            'error': failure.value.__class__.__name__,
            'error_message': repr(failure.value),
            'crawled_at': time.time(),
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Check all URLs and append status results "
                    "to the output file."
    )
    parser.add_argument("urls", help="A file with urls to check, an url per line")
    parser.add_argument("result", help="Result file, e.g. items.jl")
    args = parser.parse_args()

    cp = CrawlerProcess(dict(
        ROBOTSTXT_OBEY=False,
        CONCURRENT_REQUESTS_PER_IP=1,
        CONCURRENT_REQUESTS=48,
        DOWNLOAD_DELAY=2,
        MEMUSAGE_ENABLED=True,
        FEED_FORMAT='jsonlines',
        FEED_URI=args.result,
        LOG_FILE='spider.log',
        LOG_LEVEL='INFO',
        DUPEFILTER_CLASS='scrapy.dupefilters.BaseDupeFilter',
    ))
    cp.crawl(LinkrotSpider, urls=args.urls)
    cp.start()

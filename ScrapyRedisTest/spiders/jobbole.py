# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from urllib import parse


class JObboleSpider(RedisSpider):

    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    redis_key = 'jobbole:start_urls'
    # start_urls = ['http://blog.jobbole.com/all-posts/']

    # 收集伯乐在线所有404的url以及404页面数
    handle_httpstatus_list = [404, 302]

    def __init__(self):
        self.fail_urls = []

    def parse(self, response):
        """
        1.获取文章列表中的文章url并交给scrapy下载后进行解析
        2.获取下一页url并交给scrapy下载，下载完后交给parse函数
        """
        if response.status == 404 or response.status == 302:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        # 解析页面文章url并交给scrapy下载后进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front-img-url": image_url},
                          callback=self.parse_detail)
            print(post_url)

        # 提取下一页url并交给scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        pass
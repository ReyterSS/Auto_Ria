# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class RiaVwSpider(CrawlSpider):
    name = "ria_vw"
    start_urls = [
        'https://auto.ria.com/uk/newauto/category-legkovie/body-krossover/marka-volkswagen/model-touareg'
    ]

    rules = [
        Rule(LinkExtractor(allow="page=")),
        Rule(LinkExtractor(allow='auto-volkswagen-touareg'), callback='parse_item', process_links='process_links')
    ]

    def process_links(self, links):
        # Process links to ensure correct format
        for link in links:
            if link.url.startswith('https://auto.ria.com/'):
                link.url = link.url.replace('https://auto.ria.com/', 'https://auto.ria.com/uk/')
        return links

    def extract_with_xpath(self, response, *xpaths):
        # Helper method for extracting data using multiple XPath expressions
        for xpath in xpaths:
            data = response.xpath(f'normalize-space({xpath})').get()
            if data:
                return data.strip()
        return None

    def parse_item(self, response):
        # Check for availability of the listing
        if response.xpath('//div[@id="soldAutoCallbackDesktop"] | //*[@class="size24 mb-8 d-block"]'):
            return

        # Extracting car data with a structured approach
        car_data = {
            'Назва': self.extract_with_xpath(response,
                    '//*[@class="auto-head_title bold mb-15"]//text()',
                    '//*[@class="w500 characteristic-value underlined"]',
                    '//h1'),
            'Ціна': self.extract_with_xpath(response,
                    'normalize-space(//div[contains(@*, "price_value price_value--additional")])',
                    'normalize-space(//div[@class="mb-15"]//text())',
                    lambda x: x.strip()),
            'Колір': self.extract_with_xpath(response,
                    '//div[@class="body_color_name"]//text()',
                    '//*[contains(@*, "size16 text-r overflowed")]//text()'),
            'Продавець': self.extract_with_xpath(response,
                    '//*[@class="seller_info_name"]/a//strong//text()',
                    '//*[@*="apple-mobile-web-app-capable"]//text()'),
            'Двигун': self.extract_with_xpath(response,
                    'normalize-space(//*[@class="defines_list_title"][text()="Двигун"]/following-sibling::dd[1])',
                    None,
                    lambda x: x.strip()),
            'Потужність': self.extract_with_xpath(response,
                    '//*[contains(text(), "Потужність двигуна")]//parent::label/parent::li/*[@class="value"]//text()',
                    '//*[@*="auto-head_title mb-10"]//div[@class ="auto-head_base"]/strong/following-sibling::span//text()',
                    lambda x: x.split('(')[1].split(')')[0] if '(' in x and ')' in x else x),
            'Розгін до 100 км': self.extract_with_xpath(response,
                    '//*[(text()="Час розгону до 100 км/год")]//parent::label/parent::li/*[@class="value"]//text()',
                    '//*[(text()="Час розгону до 100 км/год")]//following-sibling::span//text()'),
            'Посилання':  response.url
        }

        yield car_data

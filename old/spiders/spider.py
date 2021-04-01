import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import OldItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class OldSpider(scrapy.Spider):
	name = 'old'
	start_urls = ['https://oldsecondbank.wordpress.com/2013/01/']

	def parse(self, response):
		post_links = response.xpath('//aside[@id="archives-2"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_months)

	def parse_months(self, response):
		links = response.xpath('//h1/a/@href').getall()
		yield from response.follow_all(links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//time[@class="entry-date"]/text()').get()
		title = response.xpath('//h1[@class="entry-title"]/text()').get()
		content = response.xpath('//div[@class="entry-content"]//text()[not (ancestor::div[@id="jp-post-flair"] or ancestor::img)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=OldItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

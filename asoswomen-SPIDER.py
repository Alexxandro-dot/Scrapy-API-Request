# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy import Spider
from scrapy.http import Request

#vorher: ShoesSpider(scrapy.Spider)
class ShoesSpider(Spider):
    name = 'asoswomen'
    allowed_domains = ['asos.com']
    start_urls = ['https://www.asos.com/women/hoodies-sweatshirts/cat/?cid=11321&ctaref=hp|ww|prime|feature|5|category|loungewear']

    def parse(self, response):
        products=response.xpath("//article[@data-auto-id='productTile']/a/@href").getall()
        for product in products:
            yield Request(product, callback=self.parse_hoodies)

        next_page_url=response.xpath("//a[text()='Load more']/@href").get()
        if next_page_url:
            yield Request (next_page_url,
                            callback=self.parse)

    def parse_hoodies(self, response): 
        #ab hier kommt API ins Spiel (weil wir den Preis nicht normal scrapen können- Produktname funktioniert)
        product_name=response.xpath("//h1/text()").get()
        product_id=response.url.split('/prd/')[1].split("?")[0]
        #das ist API Adresse von Request URL (Method:GET)
        price_api_url='https://www.asos.com/api/product/catalogue/v3/stockprice?productIds='+ product_id +'&store=COM&currency=GBP'          
        #go to json backend and extract the price from the product
        yield Request(price_api_url,
                    meta={'product_name': product_name},
                    callback=self.parse_hoodie_price)

        


    def parse_hoodie_price (self, response):
        #loads= String
        jsonresponse=json.loads(response.body.decode('utf-8'))
        #api-exctracten= siehe Excel 
        price = jsonresponse[0]['productPrice']['current']['value']
        product_code= jsonresponse[0]['productCode']
        product_id= jsonresponse[0]['productId']

        yield {
            'product_name': response.meta['product_name'],
            'price in GBP': price,
            'product_code': product_code,
            'product_id': product_id}
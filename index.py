import re
from scrapy.selector import Selector
import scrapy
import sys
from scrapy.crawler import CrawlerProcess
from dateutil import parser
import json
import logging
logging.getLogger('scrapy').propagate = False


class PumpSiteSpider(scrapy.Spider):
    name = 'PumpSite'
    custom_settings = {
        "FEED_URI": "output.csv",
        "FEED_FORMAT": "csv",
    }

    def convert_slug_to_text(self, slug):
        # Replace underscores with spaces
        text = slug.replace("-", " ")
        # Capitalize the first letter of each word
        text = text.title()
        return text

    def start_requests(self):
        with open('config.json') as f:
            urls = json.load(f)
        for originUrl in urls:
            yield scrapy.Request(url=originUrl, callback=self.parse_list, meta={'originUrl': originUrl})

    def parse_list(self, response):
        try:
            originUrl = response.meta['originUrl']
            subitem = originUrl.split('/')
            # submenu = item.submenu
            # print(submenu)
            productSelector = ".product-info-stock-sku"
            # items = response.css(productSelector).getall()
            items = response.css(productSelector).getall()
            if len(items) != 0:
                url = response.url
                productNameSelector = "div.page-title-wrapper span.base::text"
                productCodeSelector = "div.product-info-stock-sku div.value::text"
                mrpPriceSelector = "div.product-info-price span.old-price span.price::text"
                priceSelector = "span.special-price span.price::text"
                overviewSelector1 = "div.product.info.detailed div.product.attribute.description p::text"
                overviewSelector2 = "div.product.info.detailed div.product.attribute.description span::text"
                deliverySelector = "#delivery p::text"
                fullDetailHeaderSelector = "#product-attribute-specs-table th::text"
                fullDetailContentSelector = "#product-attribute-specs-table td::text"
                imgURLSelector = "div.c-gallery__thumbs img::attr(src)"
                variationSelector = "#product-options-wrapper span::text"
                variationDataSelector = "div.fieldset div.control select"
                variationDataInsideSelector = "select option::text"
                downloadSelector = "div.product-attachment-container a::attr(href)"

                productName = response.css(productNameSelector).get()
                productCode = "SKU: " + response.css(productCodeSelector).get()
                mrpPrice = "MRRP" + \
                    response.css(mrpPriceSelector).get() + " + VAT"
                price = response.css(priceSelector).get()
                overview = response.css(overviewSelector1).getall(
                ) + response.css(overviewSelector2).getall()
                delivery = response.css(deliverySelector).getall()
                fullDetailHeader = response.css(
                    fullDetailHeaderSelector).getall()
                fullDetailContent = response.css(
                    fullDetailContentSelector).getall()
                fullDetail = ""
                fullDetailindex = [-1, -1, -1, -1, -1, -1, -1, -1, -1]
                for i in range(len(fullDetailHeader)):
                    if fullDetailHeader[i] == "Manufacturer":
                        fullDetailindex[0] = i
                    if fullDetailHeader[i] == "Weight":
                        fullDetailindex[1] = i
                    if fullDetailHeader[i] == "Dimensions":
                        fullDetailindex[2] = i
                    if fullDetailHeader[i] == "Motorsize":
                        fullDetailindex[3] = i
                    if fullDetailHeader[i] == "Fullloadcurrent":
                        fullDetailindex[4] = i
                    if fullDetailHeader[i] == "Voltage":
                        fullDetailindex[5] = i
                    if fullDetailHeader[i] == "Max Flow":
                        fullDetailindex[6] = i
                    if fullDetailHeader[i] == "Max Head":
                        fullDetailindex[7] = i
                    if fullDetailHeader[i] == "Material":
                        fullDetailindex[8] = i

                    fullDetailHeader[i] = fullDetailHeader[i].strip()
                    fullDetailContent[i] = fullDetailContent[i].strip()
                    fullDetail += f'{fullDetailHeader[i]} : {fullDetailContent[i]}\n'
                imgURL = response.css(imgURLSelector).getall()
                variation = response.css(variationSelector).getall()
                variationSelect = response.css(variationDataSelector)

                def format(string):
                    return re.sub(r'[\n ]+', ' ', string)

                variationText = []
                for select in variationSelect:
                    data = select.css(variationDataInsideSelector).getall()[1:]
                    formatData = list(map(format, data))
                    variationText.append(formatData)
                download = response.css(downloadSelector).getall()
                yield {
                    "URL": url,
                    "main": self.convert_slug_to_text(subitem[3]),
                    "Sub Category-1": self.convert_slug_to_text(subitem[4]),
                    "Sub Category-2": self.convert_slug_to_text(subitem[5]),
                    "Product Name": productName,
                    "Product Code": productCode,
                    "Mrp price": mrpPrice,
                    "Price": price,
                    "Overview & Spec": overview[0] if len(overview) > 0 else "",
                    "DELIVERY & RETURNS": delivery[0] if len(delivery) > 0 else "",
                    "Full details of table content": fullDetail,
                    "Manufacturer": fullDetailContent[fullDetailindex[0]] if fullDetailindex[0] != -1 else "",
                    "Weight": fullDetailContent[fullDetailindex[1]] if fullDetailindex[1] != -1 else "",
                    "Dimensions": fullDetailContent[fullDetailindex[2]] if fullDetailindex[2] != -1 else "",
                    "Motorsize": fullDetailContent[fullDetailindex[3]] if fullDetailindex[3] != -1 else "",
                    "Full load current": fullDetailContent[fullDetailindex[4]] if fullDetailindex[4] != -1 else "",
                    "Voltage": fullDetailContent[fullDetailindex[5]] if fullDetailindex[5] != -1 else "",
                    "Max Flow": fullDetailContent[fullDetailindex[6]] if fullDetailindex[6] != -1 else "",
                    "Max Head": fullDetailContent[fullDetailindex[7]] if fullDetailindex[7] != -1 else "",
                    "Material": fullDetailContent[fullDetailindex[8]] if fullDetailindex[8] != -1 else "",
                    "Image url-1": imgURL[0] if len(imgURL) > 0 else "",
                    "Image url-2": imgURL[1] if len(imgURL) > 1 else "",
                    "Image url-3": imgURL[2] if len(imgURL) > 2 else "",
                    "Image url-4": imgURL[3] if len(imgURL) > 3 else "",
                    "Image url-5": imgURL[4] if len(imgURL) > 4 else "",
                    "Image url-6": imgURL[5] if len(imgURL) > 5 else "",
                    "Image url-7": imgURL[6] if len(imgURL) > 6 else "",
                    "Variation option-1 name": variation[0] if len(variation) > 0 else "",
                    "Variation option-2 name": variation[1] if len(variation) > 1 else "",
                    "Variation option-1": variationText[0][0] if len(variation) > 0 and len(variationText[0]) > 1 else "",
                    "Variation option-2": variationText[0][1] if len(variation) > 0 and len(variationText[0]) > 2 else "",
                    "Variation option-3": variationText[0][2] if len(variation) > 0 and len(variationText[0]) > 3 else "",
                    "Variation option-4": variationText[0][3] if len(variation) > 0 and len(variationText[0]) > 4 else "",
                    "Variation option-5": variationText[0][4] if len(variation) > 0 and len(variationText[0]) > 5 else "",
                    "Variation option-6": variationText[0][5] if len(variation) > 0 and len(variationText[0]) > 6 else "",
                    "Variation option-7": variationText[0][6] if len(variation) > 0 and len(variationText[0]) > 7 else "",
                    "Variation option-8": variationText[0][7] if len(variation) > 0 and len(variationText[0]) > 8 else "",
                    "Variation option-9": variationText[0][8] if len(variation) > 0 and len(variationText[0]) > 9 else "",
                    "2 variation option-1": variationText[1][0] if len(variation) > 1 and len(variation) > 1 else "",
                    "3 variation option-1": variationText[1][1] if len(variation) > 1 and len(variation) > 2 else "",
                    "4 variation option-1": variationText[1][2] if len(variation) > 1 and len(variation) > 3 else "",
                    "5 variation option-1": variationText[1][3] if len(variation) > 1 and len(variation) > 4 else "",
                    "6 variation option-1": variationText[1][4] if len(variation) > 1 and len(variation) > 5 else "",
                    "7 variation option-1": variationText[1][5] if len(variation) > 1 and len(variation) > 6 else "",
                    "8 variation option-1": variationText[1][6] if len(variation) > 1 and len(variation) > 7 else "",
                    "9 variation option-1": variationText[1][7] if len(variation) > 1 and len(variation) > 8 else "",
                    "File Downloads link-1": download[0] if len(download) > 0 else "",
                    "File Downloads link-2": download[1] if len(download) > 1 else "",
                    "File Downloads link-3": download[2] if len(download) > 2 else "",
                    "File Downloads link-4": download[3] if len(download) > 3 else "",
                }
                return
            productSelector = "div.category-intro__heading-inner h1::text"
            productSelector = ".page-main a::attr(href)"
            items = response.css(productSelector).getall()
            for item in items:
                if item.find("https:") != -1:
                    yield scrapy.Request(url=item, callback=self.parse_list, meta={'originUrl': originUrl})
                    pass
        except Exception as e:
            print("=====>error", e)
        pass

    def getInfo(self, response):
        nameSelector = ".product-meta h1::text"
        skuSelector = ".product-meta__sku-number::text"
        priceSelector = ".price-list span"

        name = response.css(nameSelector).get()
        sku = "SKU" + response.css(skuSelector).get()
        price = response.css(priceSelector).get().split("</span>")[1]
        yield {
            "Product Name": name,
            "SKU": sku,
            "Price": price,
            "Website name": "https://rckongen.dk/"
        }


process = CrawlerProcess()
process.crawl(PumpSiteSpider)
process.start()

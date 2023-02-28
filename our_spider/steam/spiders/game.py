from scrapy import Spider, Request
from scrapy.http import HtmlResponse

class GameSpider(Spider):
    name = 'game'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['http://store.steampowered.com/']
    platforms = []

    def GetPrice(self, p:str):
        if p.lower() == 'free' or p.lower() == 'free to play' or p.lower() == 'free movie':
            return p
        new_price = ""
        a = '123456789$'
        for l in p:
            if l in a:
                new_price += l
        return new_price

    def CorrectMark(self, mark: str):
        d = {
            '\r\n\t\t\t\tThere are no reviews for this product\t\t\t' : 'There are no reviews for this product',
            '1 user reviews' : 'not enough reviews to put a mark',
        }
        if mark not in d.keys():
            return mark
        return d[mark]

    def start_requests(self):
        for i in range(3):
            request = input()
            new_url = f"https://store.steampowered.com/search/?term={request}&force_infinite=1&&start=50&count=100"
            yield Request(new_url, callback=self.parse)

    def parse(self, response:HtmlResponse, **kwargs):
        for href in response.xpath('//div[@id="search_resultsRows"]/a//@href').extract():
            if 'bundle' not in href:
                yield Request(href, callback=self.parse_game, cb_kwargs={'platform':[plt.split()[-1] for plt in response.xpath(f'//a[starts-with(@href, "{href}")]/div[@class="responsive_search_name_combined"]/div[@class="col search_name ellipsis"]/div/span//@class').extract()]})

    def parse_game(self, response:HtmlResponse , **kwargs):
        if "agecheck" not in response.url:
            date = response.xpath('//div[@class="date"]//text()').extract()
            date1 = []
            if len(date) != 0:
                date1 = date[0].split()
            if len(date1) > 0 and (date[0] == "TBA" or date[0] == 'Coming soon' or date1[-1] > '2000'):
                items = {
                    'name': response.xpath("//div[contains(@class,'apphub_AppName') and contains(@id,'appHubAppName')]/text()").extract_first(),
                    'date': date[-1]
                }
                mark = response.xpath("//div[contains(@class,'noReviewsYetTitle') or contains(@class,'game_review_summary positive') or contains(@class,'game_review_summary mixed') or contains(@class, 'game_review_summary not_enough_reviews')]/text()").extract()
                if len(mark) == 0:
                    mark = response.xpath("//span[contains(@class,'noReviewsYetTitle') or contains(@class,'game_review_summary positive') or contains(@class,'game_review_summary mixed') or contains(@class, 'game_review_summary not_enough_reviews')]/text()").extract()
                mark[0] = self.CorrectMark(mark[0])
                items['mark'] = mark[0]
                amount_of_comments = response.xpath('//*[@id="review_histogram_rollup_section"]/div[1]/div/span[2]/text()').extract_first()
                if amount_of_comments is None or amount_of_comments == '':
                    items['reviews'] = 'There are no reviews'
                else:
                    items['reviews'] = amount_of_comments.split()[0][1::]
                price = response.xpath('//div[contains(@class,"game_purchase_price price") or contains(@class,"discount_original_price")]//text()').extract()
                if not price:
                    items['price'] = "don't have price"
                else:
                    items['price'] = self.GetPrice(price[-1].strip())
                developers = response.xpath('//div[contains(@class, "summary column") and contains(@id, "developers_list")]/a//text()').extract()
                if len(developers) == 0:
                    items['developers'] = 'developers are not specified'
                else:
                    items['developers'] = '; '.join(developers)
                items['platforms'] = "; ".join(response.cb_kwargs['platform'])
                items['tags'] = "; ".join([tag.strip() for tag in response.xpath("//div[@class='glance_tags popular_tags']/a//text()").extract()])
                categories = response.xpath('//div[@class="blockbg"]/a//text()').extract()
                if len(categories) == 2:
                    categories.insert(1,"not categories")
                items['categories'] = " -> ".join([categories[i] for i in range(len(categories)) if i != 0 and i != len(categories) - 1])
                yield items

import scrapy
import re
import datetime


class ExampleSpider(scrapy.Spider):
    name = "navernews"

    search_word = '금리'
    start_date =  datetime.datetime(year=2005, month=5, day=1)
    current_date = start_date
    end_date = datetime.datetime(year=2020, month=7, day=14)
    page_number = 0

    start_urls = [
        'https://search.naver.com/search.naver?where=news&query=금리&sm=tab_opt&ds=2005.05.01&de=2005.05.01&docid=&nso=so%3Ar%2Cp%3Afrom20050501to20050501%2Ca%3Aall&start=1',
    ]

    final_page = 0
    def parse(self, response):
        global final_page
        
        if self.page_number == 0:
            page_text = response.css('div.title_desc span::text').get()
            total_page = re.search('(?<=\/ ).*(?=건)', page_text)
            page_result = int(page_text[total_page.start():total_page.end()])
            final_page = page_result/10
            
        for news in response.css('ul.type01 li'):
            office_name = news.css('span._sp_each_source::text').get()
            news_url = news.css('dl dt a::attr(href)').get()
            if office_name == '연합뉴스' :
                if news_url.count('yonhapnews') > 0:
                    yield scrapy.Request(news_url, callback=self.article_yn)
                else:
                    yield scrapy.Request(news_url, callback=self.article_com)
            elif office_name == '연합인포맥스' :
                if news_url.count('einfomax') > 0:
                    yield scrapy.Request(news_url, callback=self.article_yi)
                else:
                    yield scrapy.Request(news_url, callback=self.article_com)
            elif office_name == '이데일리' :
                if news_url.count('edaily') > 0:
                    yield scrapy.Request(news_url, callback=self.article_ed)
                else:
                    yield scrapy.Request(news_url, callback=self.article_com)
        
        
        if self.page_number <= final_page :
            self.page_number += 1
            thisdate1 = self.current_date.strftime('%Y.%m.%d')
            thisdate2 = self.current_date.strftime('%Y%m%d')
            next_page = 'https://search.naver.com/search.naver?&where=news&query={0}&ds={1}&de={1}&nso=so:da,p:from{2}to{2},a:all&start={3}'.format(self.search_word, 
                thisdate1, thisdate2, self.page_number*10+1)
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        else :
            self.current_date += datetime.timedelta(days=1)
            if self.current_date != self.end_date:
                self.page_number = 0
                thisdate1 = self.current_date.strftime('%Y.%m.%d')
                thisdate2 = self.current_date.strftime('%Y%m%d')
                next_page = 'https://search.naver.com/search.naver?&where=news&query={0}&ds={1}&de={1}&nso=so:da,p:from{2}to{2},a:all&start={3}'.format(self.search_word, 
                thisdate1, thisdate2, self.page_number*10+1)
                
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def article_com(self, response): # 네이버뉴스 redirection
        yield {
            'date' : response.css('div.sponsor span.t11::text').get(),
            'office' : response.css('div.press_logo a img::attr(title)').get(),
            'text' : response.css('div#articleBodyContents::text').getall()
        }
    def article_yi(self, response): # 연합인포맥스 url에 ' ' 포함
        yield {
            'date' : response.css('div.info-text ul.no-bullet li::text').getall()[1],
            'office' : '연합인포맥스',
            'text' : response.css('div#article-view-content-div::text').getall()
        }
    def article_yn(self, response): # 연합뉴스 url에 ' ' 포함
        yield {
            'date' : response.css('p.update-time::text').get(),
            'office' : '연합뉴스',
            'text':response.css('div.story-news::text').getall()
        }
    def article_ed(self, response): # 이데일리 url에 ' ' 포함
        yield {
            'date' : response.css('div.dates ul li p::text').getall()[0],
            'office' : '이데일리',
            'text' : response.css('div.news_body::text').getall()
        }
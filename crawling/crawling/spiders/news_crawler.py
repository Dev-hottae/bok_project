import scrapy
import re
import datetime
import pandas as pd
import tqdm


class ExampleSpider(scrapy.Spider):

    name = "navernews"

    search_word = '금리'
    start_date =  datetime.datetime(year=2012, month=1, day=1)
    end_date = datetime.datetime(year=2012, month=1, day=1)
    cur_page = 1
    final_page = 0

    start_urls = [
        'https://search.naver.com/search.naver?&where=news&query=%EA%B8%88%EB%A6%AC&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=3&ds=2005.05.01&de=2005.05.01&docid=&nso=so:r,p:from20120101to20121231,a:all&mynews=0&cluster_rank=34&start=1'
    ] 

    def parse(self, response):
        
        # 이번페이지 크롤링
        for news_container in response.css('ul.type01 > li'):
            office_name = news_container.css('span._sp_each_source::text').get()
            news_url = news_container.css('dl dt a::attr(href)').get()

            # print(office_name, news_url)

            if (office_name == '연합뉴스' or office_name == '연합인포맥스' or office_name == '이데일리') and (news_url[:22] in 'https://news.naver.com/'):
                yield scrapy.Request(news_url, callback=self.article_com)

            elif office_name == '연합뉴스' :
                yield scrapy.Request(news_url, callback=self.article_yn)

            elif office_name == '연합인포맥스':
                yield scrapy.Request(news_url, callback=self.article_yi)

            elif office_name == '이데일리' :
                yield scrapy.Request(news_url, callback=self.article_ed)

            else:
                pass

        # 현재 페이지정보
        page_text = response.css('div.title_desc span::text').get()
        total_page = re.search('(?<=\/ ).*(?=건)', page_text)

        ExampleSpider.final_page = int(page_text[total_page.start():total_page.end()])
                
        # 마지막 페이지 도착 이전까지
        if ExampleSpider.cur_page < ExampleSpider.final_page:

            # 다음페이지 정보로 업데이트
            ExampleSpider.cur_page += 10

            # 다음페이지 호출

            str_date = ExampleSpider.start_date.strftime("%Y%m%d")
            dot_date = str_date[:4]  +'.' + str_date[4:6] + '.' + str_date[6:]

            next_page_url = 'https://search.naver.com/search.naver?&where=news&query=%EA%B8%88%EB%A6%AC&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={0}&de={0}&docid=&nso=so:r,p:from{1}to{1},a:all&mynews=0&cluster_rank=34&start={2}'.format(dot_date,str_date, str(ExampleSpider.cur_page))

            yield scrapy.Request(next_page_url, callback=self.parse)

        else:
            # 페이지 없음
            # 날짜 업데이트
            ExampleSpider.start_date += datetime.timedelta(days=1)
            if ExampleSpider.start_date <= ExampleSpider.end_date:
                # 신규 날짜로 1번 페이지 부터 재호출
                ExampleSpider.cur_page = 1

                str_date = ExampleSpider.start_date.strftime("%Y%m%d")
                dot_date = str_date[:4]+'.'+str_date[4:6]+'.'+str_date[6:]
                
                next_date_url = 'https://search.naver.com/search.naver?&where=news&query=%EA%B8%88%EB%A6%AC&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={0}&de={0}&docid=&nso=so:r,p:from{1}to{1},a:all&mynews=0&cluster_rank=34&start={2}'.format(dot_date,str_date, str(ExampleSpider.cur_page))

                yield scrapy.Request(next_date_url, callback=self.parse)

            else:
                print("크롤링 종료")
                return

    # 네이버뉴스 redirection
    def article_com(self, response): 

        data = {
            'date' : response.css('div.sponsor span.t11::text').get(),
            'office' : response.css('div.press_logo a img::attr(title)').get(),
            'text' : ' '.join(response.css('div#articleBodyContents::text').getall()).strip().replace('  ', '')
        }

        yield self.data_to_csv(data)

    # 연합인포맥스 url에 ' ' 포함
    def article_yi(self, response): 

        data = {
            'date' : response.css('div.info-text ul.no-bullet li::text').getall()[1],
            'office' : '연합인포맥스',
            'text' : ' '.join(response.css('div#article-view-content-div::text').getall()).strip().replace('  ', '')
        }

        yield self.data_to_csv(data)
        
    # 연합뉴스 url에 ' ' 포함
    def article_yn(self, response): 

        data = {
            'date' : response.css('p.update-time::text').get(),
            'office' : '연합뉴스',
            'text': ' '.join(response.css('div.story-news::text').getall()).strip().replace('  ', '')
        }

        yield self.data_to_csv(data)
        
    # 이데일리 url에 ' ' 포함
    def article_ed(self, response): 

        data = {
            'date' : response.css('div.dates ul li p::text').getall()[0],
            'office' : '이데일리',
            'text' : ' '.join(response.css('div.news_body::text').getall()).strip().replace('  ', '')
        }

        yield self.data_to_csv(data)
        
    def data_to_csv(self, data):

        data_df = pd.DataFrame()


        yield data
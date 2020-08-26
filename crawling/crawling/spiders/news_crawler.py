import time

import scrapy
import re
import datetime
import pandas as pd
import tqdm


class ExampleSpider(scrapy.Spider):

    name = "navernews"

    url_format = 'https://search.naver.com/search.naver?&where=news&query={0}&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={1}&de={1}&docid=&nso=so:r,p:from{2}to{3},a:all&mynews=0&cluster_rank=34&start={4}'

    def __init__(self, query='', start_date='', end_date='', time_break=0, **kwargs):

        super().__init__(**kwargs)

        self.query = query
        self.time_break = time_break

        self.start_date = datetime.datetime.strptime(start_date, "%Y%m%d")
        self.end_date = datetime.datetime.strptime(end_date, "%Y%m%d")

        self.cur_page = 1
        self.final_page = 0

        dot_start_date = start_date[:4] + '.' + start_date[4:6] + '.' + start_date[6:]

        self.start_urls = [
            ExampleSpider.url_format.format(self.query, dot_start_date, start_date, end_date, self.cur_page)
        ]

    def parse(self, response):

        # 이번페이지 크롤링
        for news_container in response.css('ul.type01 > li'):
            # 타임 브레이커
            time.sleep(self.time_break)
            office_name = news_container.css('span._sp_each_source::text').get()
            news_url = news_container.css('dl dt a::attr(href)').get()

            # print(office_name, news_url)

            if (office_name == '연합뉴스' or office_name == '연합인포맥스' or office_name == '이데일리') and (
                    'news.naver.com/' in news_url):
                yield scrapy.Request(news_url, callback=self.article_com, cb_kwargs=dict(url=news_url))

            elif office_name == '연합뉴스':
                yield scrapy.Request(news_url, callback=self.article_yn, cb_kwargs=dict(url=news_url))

            elif office_name == '연합인포맥스':
                yield scrapy.Request(news_url, callback=self.article_yi, cb_kwargs=dict(url=news_url))

            elif office_name == '이데일리':
                yield scrapy.Request(news_url, callback=self.article_ed, cb_kwargs=dict(url=news_url))

            else:
                pass

        # 현재 페이지정보
        page_text = response.css('div.title_desc span::text').get()
        total_page = re.search('(?<=\/ ).*(?=건)', page_text)

        self.final_page = int(page_text[total_page.start():total_page.end()].replace(',', ''))

        # 마지막 페이지 도착 이전까지
        if self.cur_page < self.final_page:

            # 다음페이지 정보로 업데이트
            self.cur_page += 10

            # 다음페이지 호출

            str_date = self.start_date.strftime("%Y%m%d")
            dot_date = str_date[:4] + '.' + str_date[4:6] + '.' + str_date[6:]

            next_page_url = 'https://search.naver.com/search.naver?&where=news&query={0}&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={1}&de={1}&docid=&nso=so:r,p:from{2}to{2},a:all&mynews=0&cluster_rank=34&start={3}'.format(
                self.query, dot_date, str_date, str(self.cur_page))

            yield scrapy.Request(next_page_url, callback=self.parse)

        else:
            # 페이지 없음
            # 날짜 업데이트
            self.start_date += datetime.timedelta(days=1)
            if self.start_date <= self.end_date:
                # 신규 날짜로 1번 페이지 부터 재호출
                self.cur_page = 1

                str_date = self.start_date.strftime("%Y%m%d")
                dot_date = str_date[:4] + '.' + str_date[4:6] + '.' + str_date[6:]

                next_date_url = 'https://search.naver.com/search.naver?&where=news&query={0}&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={1}&de={1}&docid=&nso=so:r,p:from{2}to{2},a:all&mynews=0&cluster_rank=34&start={3}'.format(
                    self.query, dot_date, str_date, str(self.cur_page))

                yield scrapy.Request(next_date_url, callback=self.parse)

            else:
                print("크롤링 종료")
                return

    # 네이버뉴스 redirection
    def article_com(self, response, url):

        yield {
            'date': re.search('[0-9]{4}[\.\-]?[0-9]{2}[\.\-]?[0-9]{2}',
                              response.css('div.sponsor span.t11::text').get()).group(),
            'office': response.css('div.press_logo a img::attr(title)').get(),
            'url' : url,
            'text': ' '.join(response.css('div#articleBodyContents::text').getall()).strip().replace('\n', ' ').replace(
                '\\', ' ').replace('\"', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')
        }

    # 연합인포맥스 url에 ' ' 포함
    def article_yi(self, response, url):

        yield {
            'date': re.search('[0-9]{4}[\.\-]?[0-9]{2}[\.\-]?[0-9]{2}',
                              response.css('div.info-text ul.no-bullet li::text').getall()[1]).group(),
            'office': '연합인포맥스',
            'url' : url,
            'text': re.sub('(\<[^\<\>]*\>)', ' ',
                           response.css('div#article-view-content-div').getall()[0]).strip().replace('\n', ' ').replace(
                '\\', ' ').replace('\"', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')
        }

    # 연합뉴스 url에 ' ' 포함
    def article_yn(self, response, url):

        yield {
            'date': re.search('[0-9]{4}[\.\-]?[0-9]{2}[\.\-]?[0-9]{2}',
                              response.css('p.update-time::text').get()).group(),
            'office': '연합뉴스',
            'url' : url,
            'text': re.sub('(\<[^\<\>]*\>)', ' ', response.css('div.story-news').getall()[0]).strip().replace('\n',
                                                                                                              ' ').replace(
                '\\', ' ').replace('\"', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')
        }

    # 이데일리 url에 ' ' 포함
    def article_ed(self, response, url):

        yield {
            'date': re.search('[0-9]{4}[\.\-]?[0-9]{2}[\.\-]?[0-9]{2}',
                              response.css('div.dates ul li p::text').getall()[0]).group(),
            'office': '이데일리',
            'url' : url,
            'text': ' '.join(response.css('div.news_body::text').getall()).strip().replace('\n', ' ').replace('\\',
                                                                                                              ' ').replace(
                '\"', ' ').replace('\r', ' ').replace('\t', ' ').replace('  ', ' ')
        }

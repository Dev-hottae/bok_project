[한국은행 NLP 구현 프로젝트] bok_project
=============
> 관련참고 
> https://www.bok.or.kr/portal/bbs/P0002454/view.do?nttId=10049321&menuNo=200431&pageIndex=2

### 프로젝트 내려받기
```python
git clone 'https://github.com/Dev-hottae/bok_project.git'
```

## 0. requirements.txt 로 패키지 다운로드
```
pip install -r requirements.txt
```

## 1. news_crawler 
### crawling 디렉토리로 이동
```
cd crawling
```

### scrapy 크롤러 동작 명령어
```
scrapy crawl navernews                # csv 형식으로 저장(default)
scrapy crawl navernews -o test.json   # json 형식으로 저장
```

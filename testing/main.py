import BOK
from ngram.ngram import ngram
import pandas as pd
import itertools
import datetime
import re
import numpy as np 

# 학습 DATA 불러오기
# ※파일 위치 지정
train_data = pd.read_json('final_ngram_comma.json')
train_data['date'] = list(map(lambda i : i.date(), train_data['date']))
train_data.set_index('date', inplace=True)
# 학습 기간 설정
train_data = train_data.iloc[(train_data.index >= datetime.date(2005,5,1)) & 
                            (train_data.index <= datetime.date(2017,12,31))]
# 클래스 사용 위해 데이터 분리
train_data['ngram'] = list(map(lambda i : i.split(','), train_data['ngram']))


# n그램 개수 counting
def useful_ngram(x):
    a = 0
    b = 0
    for ngram in x:
        if ngram in hawkish:
            a += 1
        elif ngram in dovish:
            b += 1
    return a+b
# final_test['useful'] = list(map(useful_ngram, final_test['ngram']))

# 일자 별 유의미한 Ngram 개수가 너무 적을 경우 해당 날짜 이상치 발생 방지
ngram_limit = 5
def tone_sent(x):
    a = 0
    b = 0
    for ngram in x:
        if ngram in hawkish:
            a += 1
        elif ngram in dovish:
            b += 1
    if a+b < ngram_limit:
        return np.nan
    try:
        return (a-b) / (a+b)
    except:
        return np.nan

corr_result = []
# 기준 금리 데이터, 경로 설정
sr_df = pd.read_json('standard_rate.json').set_index('date')

# Load Test Data, 날짜 하나로 NGRAM 합침
test_data = pd.read_json('test_ngram_datas.json')
test_data['ngram'] = list(map(lambda i : i.split(','), test_data['ngram']))
test_data['date'] = list(map(lambda i : i.date(), test_data['date']))
test_data = test_data[test_data['date'] <= datetime.date(2017,12,31)]

test_date_list = list(set(list(test_data['date'])))
final_test = pd.DataFrame(test_date_list, columns=['date'])

# Ngram 하루에 합침
final_test['ngram'] = list(map(lambda i : list(itertools.chain(*test_data[test_data['date'] == i]['ngram'])), test_date_list))
# Ngram 개수 Counting
# final_test['count'] = list(map(lambda i : len(i), final_test.sort_values('date')['ngram']))
final_test.set_index('date', inplace=True)
final_test.sort_index(inplace=True)

test_data = pd.read_json('test_ngram_datas.json')
test_data['ngram'] = list(map(lambda i : i.split(','), test_data['ngram']))
test_data['date'] = list(map(lambda i : i.date(), test_data['date']))
test_data = test_data[test_data['date'] <= datetime.date(2017,12,31)]


ng = ngram()
# 금리 폴더 내부의 학습할 금리 json 파일 리스트에 저장 
# ex) 30일, 0.03 & 25일, 0.02 등
ng.search('rate_data')

for file in ng.file_list:
    cd_df = pd.read_json(file)
    cd_df['date'] = list(map(lambda i : i.date(), cd_df['date']))
    cd_df.set_index('date', inplace=True)

    train_data['ud'] = cd_df['ud']
    nbc = BOK.NBC()
    nbc.add_data(train_data)
    nbc.bagging(train_data, 30)
    nbc.df = nbc.df[nbc.df[[1,0,-1]].sum(axis=1) > 15] # 빈도 수 15개 미만 NGRAM 자르기

    hawkish = nbc.df[nbc.df['score'] >= 1.3].index
    dovish = nbc.df[nbc.df['score'] <= 10/13].index

    # Tone 계산 (문장 -> 문서)
    test_data['tone'] = list(map(tone_sent, test_data['ngram']))
    tone_data = test_data.dropna()
    # 0은 중립
    test_data['HD'] = list(map(lambda i : 'H' if i > 0 else 'D' if i < 0 else np.nan, test_data['tone']))
    test_data.dropna(inplace=True)
    test_data['H'] = list(map(lambda i : 1 if i == 'H' else 0, test_data['HD']))
    test_data['D'] = list(map(lambda i : 1 if i == 'D' else 0, test_data['HD']))
    final_tone = test_data.groupby('date').sum()[['H','D']]
    final_tone['tone'] = (final_tone['H'] - final_tone['D']) / (final_tone['H'] + final_tone['D'])
    final_tone['rate'] = sr_df['rate']

    # Tone 계산 (일자 Ngram 합친 문서 Tone 계산 1회)
    final_test['tone'] = list(map(tone_sent, final_test['ngram']))
    final_test.dropna(inplace=True)
    sr_df = pd.read_json('standard_rate.json').set_index('date')
    final_test['rate'] = sr_df['rate']

    # 상관분석
    corr = final_tone[['tone','rate']].corr(method = 'pearson')
    rate_title = re.search('[0-9].*(?=\.json)', file)
    rate_title = rate_title.group()
    print(rate_title, len(final_tone), corr, sep = '\n')
    corr_result.append(corr)





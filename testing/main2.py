import BOK
import pandas as pd
import itertools
import datetime
import re
import numpy as np 

# 합친 뒤 Tone 문서

# 학습 DATA 불러오기
# ※파일 위치 지정
train_data = pd.read_json('testing/final_ngram_comma.json')
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

test_data = pd.read_json('testing/test_ngram_datas.json')
test_data['ngram'] = list(map(lambda i : i.split(','), test_data['ngram']))
test_data['date'] = list(map(lambda i : i.date(), test_data['date']))
test_data = test_data[test_data['date'] <= datetime.date(2017,12,31)]

test_date_list = list(set(list(test_data['date'])))
final_test = pd.DataFrame(test_date_list, columns=['date'])

final_test.set_index('date', inplace=True)
final_test.sort_index(inplace=True)

# Ngram 하루에 합침 (최종 테스트 데이터)
final_test['ngram'] = list(map(lambda i : list(itertools.chain(*test_data[test_data['date'] == i]['ngram'])), test_date_list))
# Ngram 개수 Counting
# final_test['count'] = list(map(lambda i : len(i), final_test.sort_values('date')['ngram']))

# 일자 별 유의미한 Ngram 제한, 개수가 너무 적을 경우 해당 날짜 이상치 발생 방지
# 개수 확인 필요 하위 25%가 몇개인지 최소 150개는 가져가야 하지 않나
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


call_corr = []
# 기준 금리 데이터, 경로 설정
sr_df = pd.read_json('testing/standard_rate.json').set_index('date')

# 금리 Raw 데이터에서 기간, 금리 변동 별로 Labeling 하면서 최적값 탐색
call_datas = pd.read_json('testing/rate_data/call_raw.json')
date_count = range(2, 31)
rate_limit = [0.01, 0.02, 0.03, 0.04, 0.05]

for d in date_count:
    for r in rate_limit:
        print('현재 진행 날짜 :', d,'\n현재 진행 Rate_Limit :', r)
        train_data['ud'] = BOK.rate_label(call_datas, d, r)['ud']
        
        nbc = BOK.NBC()
        nbc.add_data(train_data)
        nbc.bagging(train_data, 30)
        nbc.df = nbc.df[nbc.df[[1,0,-1]].sum(axis=1) > 15] # 빈도 수 15개 이하 NGRAM 자르기

        hawkish = nbc.df[nbc.df['score'] >= 1.3].index
        dovish = nbc.df[nbc.df['score'] <= 10/13].index

        print(len(hawkish), len(dovish))

        # Tone 계산 (일자 Ngram 합친 문서 Tone 계산 1회)
        final_test['tone'] = list(map(tone_sent, final_test['ngram']))
        tone_data = final_test.dropna()
        tone_data['rate'] = sr_df['rate']

        # 상관분석
        corr = tone_data['tone'].corr(tone_data['rate'], method = 'pearson')
        call_corr.append([d, r, len(tone_data), corr])
        print('Date Range:', d, "Rate Limit:", r, '\nTest 개수:', len(tone_data), 'corr', corr)
        print()


pd.DataFrame(call_corr, columns = ['Date_Range', 'Rate_Limit', 'doc_count', 'Corr']).to_json('doc_call_corr.json')


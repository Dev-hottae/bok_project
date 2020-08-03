import BOK
import pandas as pd
import itertools
import datetime
import re
import numpy as np 

# 문장 -> 문서

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

# 일자 별 유의미한 Ngram 제한, 개수가 너무 적을 경우 해당 날짜 이상치 발생 방지
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
sr_df = pd.read_json('testing/standard_rate.json').set_index('date')

# Load Test Data, 날짜 하나로 NGRAM 합침
test_data = pd.read_json('testing/test_ngram_datas.json')
test_data['ngram'] = list(map(lambda i : i.split(','), test_data['ngram']))
test_data['date'] = list(map(lambda i : i.date(), test_data['date']))
test_data = test_data[test_data['date'] <= datetime.date(2017,12,31)]

# 금리 Raw 데이터에서 기간, 금리 변동 별로 Labeling 하면서 최적값 탐색
call_datas = pd.read_json('testing/rate_data/call_raw.json')
date_count = range(2, 31)
rate_limit = [0.01, 0.02, 0.03, 0.04, 0.05]

call_corr = []
for dc in date_count:
    for rl in rate_limit:
        print('현재 진행 날짜 :', dc,'\n현재 진행 Rate_Limit :', rl)
        train_data['ud'] = BOK.rate_label(call_datas, dc, rl)['ud']
        
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

        # 상관분석
        corr = final_tone['tone'].corr(final_tone['rate'], method = 'pearson')
        call_corr.append([dc, rl, corr])
        print('Date Range:', dc, "Rate Limit:", rl, '\nTest 개수:', len(final_tone), 'Corr :', corr)
        print()

pd.DataFrame(call_corr, columns = ['Date_Range', 'Rate_Limit', 'Corr']).to_json('sent_doc_call_corr.json')


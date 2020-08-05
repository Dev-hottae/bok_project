from BOKpack import BOK
import pandas as pd
import itertools
import datetime
import re
import numpy as np 
import copy

# 문장 -> 문서

# Load 데이터
test = BOK.Testing()

# 상위 폴더 경로 설정
train_data, call_data, test_data, sr_df = test.load_datas('testing')

# 일자 별 유의미한 Ngram 제한, 개수가 너무 적을 경우 해당 날짜 이상치 발생 방지
# ngram_limit = 5
# 안 씀, tone 문장 수로 확인
def tone_sent(x):
    a = 0
    b = 0
    for ngram in x:
        if ngram in hawkish:
            a += 1
        elif ngram in dovish:
            b += 1
    # if a+b < ngram_limit:
    #     return np.nan
    try:
        return (a-b) / (a+b)
    except:
        return np.nan

# 금리 Raw 데이터에서 기간, 금리 변동 별로 Labeling 하면서 최적값 탐색
date_count = [i for i in range(-30,31) if i not in [-1,0,1]]
rate_limit = [0.01, 0.02, 0.03, 0.04, 0.05]
call_corr = []

for dc in date_count:
    for rl in rate_limit:
        print('현재 진행 날짜 :', dc,'\n현재 진행 Rate_Limit :', rl)
        train_data['ud'] = BOK.rate_label(call_data, dc, rl)['ud']

        nbc = BOK.NBC()
        nbc.add_data(train_data)
        nbc.bagging(train_data, 30)
        nbc.df = nbc.df[nbc.df[[1,0,-1]].sum(axis=1) > 15] # 빈도 수 15개 미만 NGRAM 자르기

        hawkish = nbc.df[nbc.df['score'] >= 1.3].index
        dovish = nbc.df[nbc.df['score'] <= 10/13].index
        print(len(hawkish), len(dovish))

        # Tone 계산 (문장 -> 문서)
        test_data['tone'] = list(map(tone_sent, test_data['ngram']))
        
        tone_data = copy.deepcopy(test_data.dropna())
        # 0은 중립
        tone_data['HD'] = list(map(lambda i : 'H' if i > 0 else 'D' if i < 0 else np.nan, tone_data['tone']))
        tone_data.dropna(inplace=True)
        tone_data['H'] = list(map(lambda i : 1 if i == 'H' else 0, tone_data['HD']))
        tone_data['D'] = list(map(lambda i : 1 if i == 'D' else 0, tone_data['HD']))
        final_tone = copy.deepcopy(tone_data.groupby('date').sum()[['H','D']])
        # 남은 문장이 sl개를 넘는 BOK 문서만 계산 (이상치 제거)
        # 10개 이하 자르면 160개 정도 나오는 것을 확인
        sl = 10
        final_tone = final_tone[final_tone['H'] + final_tone['D'] > sl]
        final_tone['tone'] = (final_tone['H'] - final_tone['D']) / (final_tone['H'] + final_tone['D'])
        final_tone['rate'] = sr_df['rate']

        # 상관분석
        corr = final_tone['tone'].corr(final_tone['rate'], method = 'pearson')
        call_corr.append([dc, rl, len(final_tone), corr])
        print('Date Range:', dc, "Rate Limit:", rl, '\nTest 개수:', len(final_tone), 'Corr :', corr)

        # Hawkish, Dovish 사전 추출
        if corr > 0.68 or corr < 0.3:
            pd.DataFrame([hawkish, dovish]).to_json('testing/dictionary/hawkish_dovish_{}_{}.json'.format(dc, rl))
        print()

# 최종 상관관계 데이터 json 추출
pd.DataFrame(call_corr, columns = ['Date_Range', 'Rate_Limit', 'doc_count', 'Corr']).to_json('testing/results/final_corr.json')

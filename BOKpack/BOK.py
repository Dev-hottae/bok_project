import pandas as pd
import numpy as np
import itertools
import nltk
import copy
import datetime
from ekonlpy.sentiment import MPCK
import os

# 패키지 임포트 오류 날 때
# 1) Ctrl + Shift + P 혹은 Cmd + Shift + P 를 누릅니다.
# 2) 창에 Python Select Interpreter 를 입력하고 선택합니다
# .vscode 폴더 생성됨 (Git에는 추가하지 말 것)

class JsonSearch():
    # 파일 검색 (폴더명 혹은 전체탐색 시 .)
    # 현재 경로 확인 필수
    def search(self, dirname):
        filenames = os.listdir(dirname)
        fl = []
        for filename in filenames:
            if '.json' in filename:
                fl.append(os.path.join(dirname, filename))
        
        self.file_list = fl
        return self.file_list

    # pandas DataFrame으로 반환
    def select_file(self, number):
        return pd.read_json(self.file_list[number])

class Ngram():
    def make_ngram(self, text):
        mpck = MPCK()
        print('ngram {} 에 대한 작업 진행 중... '.format(text[:10]))
        # Encoding 'cp949' 오류 -> 해당 파일로 들어가서 encoding='utf-8' 추가해줄 것
        tokens = mpck.tokenize(text) # text 들어갈 곳
        ngrams = mpck.ngramize(tokens)
        
        # 빈 ngram 처리, dropna 사용위함
        if ngrams == []:
            ngrams = None
        return ngrams
    
    # 만들어놓긴 했지만 POOL 사용으로 의미 X
    def split_data(self, datas):
        total_len = len(datas[datas.columns[len(datas.columns)-1]])
        lens = []
        k = 4
        d_l = []
        for i in range(1, k+1):
            lens.append(int(total_len * i / k))

        for i, l in enumerate(lens):
            if i == 0:
                d_l.append(datas.iloc[:l][datas.columns[len(datas.columns)-1]])
            else:
                d_l.append(datas.iloc[lens[i-1]:l][datas.columns[len(datas.columns)-1]])
        return d_l

class NBC():
    def add_data(self, datas):
        word_column = datas.columns[0]
        target_column = datas.columns[1]
        target_ls = list(set(datas[target_column]))
        # list가 아닐 경우 실행
        # datas[word_column] = list(map(lambda i : i.split(','), datas[word_column]))

        total_ngram = list(itertools.chain(*list(datas[word_column]))) 
        unique_ngram = list(set(total_ngram))
        result_df = pd.DataFrame(unique_ngram, columns = [word_column]).set_index(word_column)
        for target in target_ls:
            this_ngram = list(itertools.chain(*list(datas[datas[target_column] == target][word_column])))
            fdist = nltk.FreqDist(this_ngram)
            temp_df = pd.DataFrame(list(zip(fdist.keys(), fdist.values())), columns= [word_column, 'count']).set_index(word_column)
            result_df[target] = temp_df['count']
        
        result_df.fillna(0, inplace=True)
        result_df['score'] = 0
        self.df = copy.deepcopy(result_df)
        return self.df

    # 샘플된 데이터에 대한 카운트 매트릭스 생성
    def count_vec(self, datas):
        word_column = datas.columns[0]
        target_column = datas.columns[1]
        target_ls = list(set(datas[target_column]))

        total_ngram = list(itertools.chain(*list(datas[word_column]))) 
        unique_ngram = list(set(total_ngram))
        result_df = pd.DataFrame(unique_ngram, columns = [word_column]).set_index(word_column)
        
        for target in target_ls:
            this_ngram = list(itertools.chain(*list(datas[datas[target_column] == target][word_column])))
            fdist = nltk.FreqDist(this_ngram)
            temp_df = pd.DataFrame(list(zip(fdist.keys(), fdist.values())), columns= [word_column, 'count']).set_index(word_column)
            result_df[target] = temp_df['count']

        result_df.fillna(0, inplace=True)
        return result_df
    
    # BOK 극성점수 계산
    def polarity_score(self, datas):
        df = datas
        
        df['haw'] = df[1] / sum(df[1])
        df['dov'] = df[-1] / sum(df[-1])
        df['count'] = 1
        self.df['score'] += df['haw'] / df['dov']
        self.df['count'] += df['count']
        return self.df

    # 배깅하면서 나온 횟수만큼만 나눠줌 (30으로 나눠버리면 수치가 달라짐)
    # 30회 배깅
    def bagging(self, train_data, k):
        self.df['count'] = 0
        for i in range(k):
            self.polarity_score(self.count_vec(train_data.sample(frac=0.9)))

        self.df['score'] = self.df['score'] / self.df['count']
        return self.df[self.df['count'] != 0]


# 금리 라벨링 부분, 음수 Day도 사용 가능 기본값 Date_Range +28일, Limit 0.03
def rate_label(datas, dr = 28, rl = 0.03):
    temp = []
    # 금리 부분 Column rate로 통일해야 함, 라벨 부분 Column ud로 통일
    if dr < 0:
        for i in range(-dr, len(datas)):
            rate_change = float(datas['rate'][i]) - float(datas['rate'][i+dr])
            if rate_change >= rl:
                temp.append(1)
            elif rate_change <= -rl:
                temp.append(-1)
            else:
                temp.append(0)
        new_data = datas.iloc[-dr:].reset_index()
    else:
        for i in range(len(datas)-dr):
            rate_change = float(datas['rate'][i+dr]) - float(datas['rate'][i])
            if rate_change >= rl:
                temp.append(1)
            elif rate_change <= -rl:
                temp.append(-1)
            else:
                temp.append(0)
        new_data = datas.iloc[:-dr].reset_index()
    new_data['ud'] = temp
    new_data.columns = ['date', 'rate', 'ud']
    new_data['date'] = list(map(lambda i : i.date(), new_data['date']))

    # 제이슨 파일로 저장 필요 시
    # new_data.to_json('call_{}_{}.json'.format(str(dc), str(rl)))
    return new_data.set_index('date')

class Testing():
    # 파일 위치 지정 ※
    def load_datas(self, test_dir='testing'):
        # 학습 DATA 불러오기
        
        train_data = pd.read_json(test_dir+'/final_ngram_comma.json')
        train_data['date'] = list(map(lambda i : i.date(), train_data['date']))
        train_data.set_index('date', inplace=True)
        # 학습 기간 설정
        train_data = train_data.iloc[(train_data.index >= datetime.date(2005,5,1)) & 
                                    (train_data.index <= datetime.date(2017,12,31))]
        # 클래스 사용 위해 데이터 분리
        train_data['ngram'] = list(map(lambda i : i.split(','), train_data['ngram']))

        # 기준 금리 데이터, 경로 설정
        sr_df = pd.read_json(test_dir+'/standard_rate.json').set_index('date')

        # Load Test Data, 날짜 하나로 NGRAM 합침
        test_data = pd.read_json(test_dir+'/test_ngram_datas.json')
        test_data['ngram'] = list(map(lambda i : i.split(','), test_data['ngram']))
        test_data['date'] = list(map(lambda i : i.date(), test_data['date']))
        test_data = test_data[test_data['date'] <= datetime.date(2017,12,31)]

        # Load Rate Data
        call_data = pd.read_json(test_dir + '/rate_data/labeled_cd_rate.json').set_index('date')


        return train_data, call_data, test_data, sr_df

    
# 라벨링, 기타 전처리용 클래스    
# class subpre():
#     # 금리 라벨링 함수
#     def __init__(self):
#         return

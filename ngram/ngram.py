from ekonlpy.sentiment import MPCK
import os
import pandas as pd

# 패키지 임포트 오류 날 때
# 1) Ctrl + Shift + P 혹은 Cmd + Shift + P 를 누릅니다.
# 2) 창에 Python Select Interpreter 를 입력하고 선택합니다
# .vscode 폴더 생성됨 (Git에는 추가하지 말 것)

class ngram():

    file_list = []

    # 파일 검색 (폴더명 혹은 전체탐색 시 .)
    # 현재 경로 확인 필수
    def search(self, dirname):
        filenames = os.listdir(dirname)
        file_list = []
        for filename in filenames:
            if '.json' in filename:
                file_list.append(os.path.join(dirname, filename))
        
        self.file_list = file_list
        return file_list

    # pandas DataFrame으로 반환
    def select_file(self, number):
        return pd.read_json(self.file_list[number])
    
    def make_ngram(self, text):
        mpck = MPCK()
        print('ngram {} 에 대한 작업 진행 중... '.format(text[:10]))
        ## Encoding 'cp949' 오류 -> 해당 파일로 들어가서 encoding='utf-8' 추가해줄 것
        tokens = mpck.tokenize(text) # text 들어갈 곳
        ngrams = mpck.ngramize(tokens)
        return ngrams
    
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
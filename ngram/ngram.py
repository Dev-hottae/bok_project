import os
import pandas as pd
from ekonlpy.sentiment import MPCK

class ngram():
    
    file_list = []

    # 파일 검색 (폴더명 혹은 전체탐색 시 .)
    def search(self, dirname):
        filenames = os.listdir(dirname)
        file_list = []
        for filename in filenames:
            if '.json' in filename:
                file_list.append(os.path.join(dirname, filename))
        
        self.file_list = file_list
        return file_list

    # pandas DataFrame으로 반환
    def select_file(self, number)
        return pd.read_json(self.file_list[i])
    
    def make_ngram(self, text):
        mpck = MPCK()
        ## UTF-8 Encoding 오류 -> 해당 파일로 들어가서 encoding='utf-8' 추가해줄 것
        tokens = mpck.tokenize(text) # text 들어갈 곳
        ngrams = mpck.ngramize(tokens)
        
        return ngrams
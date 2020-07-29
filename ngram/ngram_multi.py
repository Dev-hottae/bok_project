import os
import pandas as pd
from tqdm import tqdm
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
    def select_file(self, number):

        return pd.read_json(self.file_list[number])


    def execute(self, data, data_start, save_dir):

        mpck = MPCK()
        data_df = pd.DataFrame([], columns=['ngram'])

        # 기존 데이터에 ngrams 칼럼 추가
        data['ngrams'] = ''

        ## UTF-8 Encoding 오류 -> 해당 파일로 들어가서 encoding='utf-8' 추가해줄 것
        for idx, text in tqdm(enumerate(data.text)):
            tokens = mpck.tokenize(text) # text 들어갈 곳
            ngrams = mpck.ngramize(tokens)

            data['ngrams'][idx] = ngrams
            for ngram in ngrams:
                data_df = data_df.append([{'ngram': ngram}], ignore_index=True)

        data.to_json(r'{}data_{}.json'.format(save_dir, data_start))
        data_df.to_json(r'{}ngram_{}.json'.format(save_dir, data_start))

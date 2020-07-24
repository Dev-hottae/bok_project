import copy

import pandas as pd
import numpy as np

class Pre_Info():

    # 클래스 생성시 파일 위치 인자로 입력
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.data = None
        self.ref_data = None

    # 파일 로드
    def load_file(self, file_name):
        self.data = pd.read_json(self.root_dir + file_name).reset_index(drop=True)

    # 지정 경로에 파일 새로저장
    def save_file(self, data, new_name):
        data.to_json(self.root_dir + new_name + '.json')

    # 현재 로드한 파일 랜덤으로 n개 추출보기 (기본값 50)
    def ran_50(self, n=50):
        print(self.data.sample(n=n))

    # 해당 인덱스 텍스트 전체보기
    def index_search(self, index):
        print(self.data.loc[index, 'text'])

    # 정규표현식 조건에 따라 파일 분할
    def file_divider(self, reg, in_file, out_file):

        # 조건에 맞으면 'condition' 컬럼에 True 추가
        self.data['condition'] = self.data.text.str.contains(reg)
        print("로드된 데이터")
        print(self.data.head())
        print("로드 데이터 길이" ,len(self.data))
        # False 인덱스 추출
        idx_false = (np.asarray(self.data[self.data['condition'] != True].index))
        print('조건 불일치 데이터 개수 : ',len(idx_false))
        copy_df = copy.deepcopy(self.data)

        out_condition = self.data.iloc[idx_false]
        in_condition = copy_df.drop(idx_false)

        self.save_file(in_condition, in_file)
        self.save_file(out_condition, out_file)

    # 정규표현식 조건에 맞는 header 부분 잘라내기
    def cutter(self, *regs):

        # # 조건에 맞는 데이터 찾기
        # reg1 = '^\([가-힣\s]+=[\s가-힣]+\)[\s가-힣]+='
        # reg2 = '^\([가-힣\s]+=[\s가-힣]+\)'
        # reg3 = '^[\sA-Za-z]+@[A-Za-z.\s]+\(끝\)'

        self.ref_data = copy.deepcopy(self.data)

        for reg in regs:
            print(reg)
            self.ref_data['text'] = self.ref_data['text'].str.replace(reg, '')
            self.ref_data['text'] = self.ref_data.text.str.strip()

    def del_useless_col(self, col):
        self.ref_data = self.data.drop([col], axis=1)

    ## text 빈 데이터 삭제
    def cut_empty(self):
        self.data['text'] = self.data.text.str.strip()
        empty_index = (np.asarray(self.data[self.data['text'] == ''].index))

        copy_df = copy.deepcopy(self.data)
        self.ref_data = copy_df.drop(empty_index)

    # 데이터 정렬
    def sort_values(self, col):
        self.ref_data = self.data.sort_values(by=[col])

    # 데이터 체크
    def check_data(self):
        print(self.data.head())
        print(self.data.tail())
        print(len(self.data))
import pandas as pd
import numpy as np


class Label():

    def __init__(self):
        self.label_file = None

    # 라벨 데이터 업로드
    def add_label_file(self, label_file):
        self.label_file = label_file

    # 라벨데이터의 상승 하락을 기준으로 1, -1 데이터화
    def label_data_processing(self):
        pass

    # 비어있는 날짜 전데이터로 맞추기
    def pre_processing(self):
        pass

    # 데이터 파일에 라벨링
    def labeling(self, data_file):
        pass


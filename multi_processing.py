import multiprocessing
import time
from collections import defaultdict

import pandas as pd


class mp():

    def __init__(self, target_class, data_dir, save_dir):
        # 타켓 클래스
        self.target_class = target_class
        # 데이터 경로(json 형태로 전달해주어야함)
        self.data_dir = data_dir
        # 데이터 저장경로
        self.save_dir = save_dir


    # 데이터 4분할
    def data_divider(self, total_part, part_num):
        # 데이터 총 길이
        # data_len = len(pd.read_json(self.data_dir))
        data_len = 80
        start_len = int(data_len * ((part_num-1)/total_part))
        fin_len = int(data_len * (part_num/total_part))

        part_data = pd.read_json(self.data_dir)[start_len:fin_len]
        print('데이터 분할 : ', part_num, '/', total_part)
        return part_data


    # 프로세싱 실행
    def execute(self, process=1):

        mp_dict = defaultdict(multi_processing)
        # 데이터 분할
        print("데이터 분할 시작!")
        for num in range(process):
            part_data = self.data_divider(process, num+1)
            mp_dict['mp_{}'.format(num)] = multi_processing(self.target_class, part_data, self.save_dir)

        print("데이터 분할 완료!")
        # 멀티프로세싱 시작
        for num in range(process):
            print("프로세스", num, "실행!")
            mp_dict['mp_{}'.format(num)].start()
            time.sleep(1)

# 멀티프로세스
class multi_processing(multiprocessing.Process):

    def __init__(self, target_class, data, save_dir):
        multiprocessing.Process.__init__(self)
        self.target_class = target_class

        # 데이터 형식은 DF로 통일
        self.data = data

        # 데이터 저장경로
        self.save_dir = save_dir

    def run(self):
        data_start = self.data.index[0]
        self.target_class.execute(self.data, data_start, self.save_dir)



# #########################
# # 클래스 선언
# if __name__ == "__main__":
#
#     data_dir = r"C:\Users\student\Desktop\newsdata\final_infomax\final_news_infomax_2018_2020.json"
#     ng = ngram()
#     mp = mp(ng, data_dir)
#     mp.execute(process=3)
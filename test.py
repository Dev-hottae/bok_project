# -*- coding: utf-8 -*-
import pandas as pd
import json
import datetime

#

# ## 데이터 중복제거
# data = pd.read_json(r'C:\Users\student\PycharmProjects\bok_project\bok_project\news_2018_2020_yeonhap.json')
# data = pd.DataFrame(data)
# print("중복제거 전 데이터 갯수 : ",len(data))
# print(data.head())
# print(data.tail())
#
# data_unique = data.drop_duplicates(['office'])
# print("중복제거 후 데이터 갯수 : ",len(data_unique))
# # data_unique.to_json('news_2005_2017_unique.json')
#####################################

# ## #####################################
# # 애매하게 들어간 날짜 지우기
# with open(r'C:\Users\student\Desktop\newsdata\news_to20200430.json', encoding='utf-8') as fh:
#     data1 = json.load(fh)
# data1_df = pd.DataFrame(data1)
# print(data1_df.head())
# print(data1_df.tail())
# print("날짜 제거전 데이터 갯수 : ",len(data1_df))
#
# idx_nm_dot = data1_df[data1_df['date'] == '2020.04.30'].index
# data1_df_del_dot = data1_df.drop(idx_nm_dot)
# print("닷데이터 제거 후 데이터 갯수 : ",len(data1_df_del_dot))
#
# idx_nm_dash = data1_df_del_dot[data1_df_del_dot['date'] == '2020-04-30'].index
# data1_df_del_dash = data1_df_del_dot.drop(idx_nm_dash)
# print("대쉬데이터 제거 후 데이터 갯수 : ",len(data1_df_del_dash))
#
# print(data1_df_del_dash.tail())
#
# data1_df_del_dash.to_json('news_20200429.json')
####################################################

####################################################
# ## text 빈 데이터 삭제
# data_df = pd.read_json(r'C:\Users\student\PycharmProjects\bok_project\bok_project\news_2005_2017_unique.json')
# print(data_df.head())
# print(data_df.tail())



####################################################
# # 데이터 합치기
# data1 = pd.read_json(r'C:\Users\student\Desktop\newsdata\news_to2013_unique.json')
# data1_df = pd.DataFrame(data1)
# data2 = pd.read_json(r'C:\Users\student\Desktop\newsdata\news_2014_2017_unique.json')
# data2_df = pd.DataFrame(data2)
# pd.merge(data1_df, data2_df, how='outer').to_json('news_2005_2017.json')


# ## 데이터 체크
# data_df = pd.read_json(r'C:\Users\student\PycharmProjects\bok_project\bok_project\news_2005_2017.json')
# print(data_df.head())
# print(data_df.tail())


# # 조건에 맞는 데이터 찾기
# data_df = pd.read_json(r'C:\Users\student\PycharmProjects\bok_project\bok_project\news_2005_2017_____edaily.json')
# idx_no_text = data_df[data_df['office'].str.strip() == '연합뉴스'].index
# print(len(idx_no_text))
# data1_df_del_notext = data_df.drop(idx_no_text)
# data1_df_del_notext.to_json('news_2018_2020_edaily.json')

# # 랜덤 데이터 추출
# data_df = pd.read_json(r'C:\Users\student\PycharmProjects\bok_project\bok_project\news_2005_2017____yeonhap.json')
# data50 = data_df.sample(n=50)
# print(data50)
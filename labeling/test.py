import json

import pandas as pd
import numpy as np

# file = pd.read_json('call_rate.json')
# # print(file)
# file['rate'] = file.call_rate
# file = file.drop(columns=['call_rate'])
# print(file)



with open('C__cs.json') as json_file:
    file = json.load(json_file)
# file['date'] = file.index
# file['call_rate'] = file['callrate']
# file = file.reset_index()
print(file)
data_list = []
# 파일 재구성
for data in reversed(file):
    data_dict = {}
    key = list(data.keys())[0]
    value = list(data.values())[0]

    data_dict['date'] = key
    data_dict['rate'] = value

    data_list.append(data_dict)


print(pd.DataFrame.from_dict(data=data_list, orient='columns'))
data = pd.DataFrame.from_dict(data=data_list, orient='columns')
# data['date'] = data.index
# data = data[['date','tr3_rate']].reset_index(drop=True).iloc[::-1].reset_index(drop=True)
# print(data)


# df.DataFrame(file)

# print(file.head())
# print(file.tail())

# file = file.drop(['callrate'], axis=1)
# file = file.drop(['index'], axis=1)
# # file = file.drop(['한달 전 callrate'], axis=1)
# # file = file.drop(['ud'], axis=1)
# #
data.to_json('cb_rate.json')
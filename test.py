# -*- coding: utf-8 -*-

import json
import datetime


with open(r'C:\Users\student\PycharmProjects\bok_project\bok_project\crawling\test.json', encoding='utf-8') as fh:
    data = json.load(fh)

print(len(data))
print(data[len(data)-1])

#########################
# import pandas as pd
# import numpy as np
#
# data_df = pd.DataFrame([], columns=['a','b','c'])
# print(data_df)

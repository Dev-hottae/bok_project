import pandas as pd
import numpy as np
import itertools
import nltk
import copy
import pandas as pd
import datetime

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

    def polarity_score(self, datas):
        df = datas
        
        df['haw'] = df[1] / sum(df[1])
        df['dov'] = df[-1] / sum(df[-1])
        df['count'] = 1
        self.df['score'] += df['haw'] / df['dov']
        self.df['count'] += df['count']
        return self.df

    # 배깅하면서 나온 횟수만큼만 나눠줌 (30으로 나눠버리면 수치가 달라짐)
    def bagging(self, train_data, k):
        self.df['count'] = 0
        for i in range(k):
            self.polarity_score(self.count_vec(train_data.sample(frac=0.9)))
        self.df['score'] = self.df['score'] / self.df['count']
        return self.df

def rate_label(datas, dc = 30, rl = 0.03):
        temp = []
        for i in range(len(datas)-dc):
            rate_change = float(datas['rate'][i+dc]) - float(datas['rate'][i])
            if rate_change >= rl:
                temp.append(1)
            elif rate_change <= -rl:
                temp.append(-1)
            else:
                temp.append(0)

        new_data = datas.iloc[:-dc].reset_index()
        new_data['ud'] = temp
        # new_data.reset_index(inplace=True)
        new_data.columns = ['date', 'rate', 'ud']
        new_data['date'] = list(map(lambda i : i.date(), new_data['date']))
        return new_data.set_index('date')
        # new_data.to_json('call_{}_{}.json'.format(str(dc), str(rl)))

    
# class subpre():
#     # 금리 라벨링 함수
#     def __init__(self):
#         return

    

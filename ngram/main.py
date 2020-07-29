import ngram
from multiprocessing import Pool
import re
import time

doc_num = 0

if __name__ == '__main__':
    ng = ngram.ngram()
    fl = ng.search('ngram\datas')
    for doc_num in range(len(fl)):
        datas = ng.select_file(doc_num)

        start_time = time.time()
        pool = Pool(processes=4)
        text_column = datas.columns[len(datas.columns)-1]
        result = pool.map(ng.make_ngram, datas[text_column])
        pool.close()
        pool.join()
        datas['ngram'] = result

        print('ngram 완료 ! 총 걸린 시간 %s seconds'%(int(time.time()- start_time)))
        temp = re.search('(?<=[s]\\\\).*(?=\.json)', fl[doc_num])
        fn = temp.group()

        datas[['date', text_column, 'ngram']].to_json('{}_ngram.json'.format(fn))
import ngram
from multiprocessing import Pool
import re
import time

doc_num = 4

if __name__ == '__main__':
    ng = ngram.ngram()
    fl = ng.search('ngram\datas')
    datas = ng.select_file(doc_num)
    start_time = time.time()
    pool = Pool(processes=3)
    result = pool.map(ng.make_ngram, datas['doc'])
    pool.close()
    pool.join()
    datas['ngram'] = result

    print('ngram 완료 ! 총 걸린 시간 %s seconds'%(int(time.time()- start_time)))
    temp = re.search('(?<=[s]\\\\).*(?=\.json)', fl[doc_num])
    fn = temp.group()

    datas[['date', 'doc', 'ngram']].to_json('{}_ngram.json'.format(fn))
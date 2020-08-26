# Call rate Labeling
import ngram
import pandas as pd

ng = ngram.ngram()
fl = ng.search(r'C:\Users\student\nlp_project\bok_project\ngram\ngram_data')

for doc_num in range(len(fl)):
    datas = ng.select_file(doc_num)
    if doc_num == 0:
        ngram_df = datas[['date', 'ngram']]
    else:
        ngram_df = pd.concat([ngram_df, datas[['date', 'ngram']]])
    
ngram_df.reset_index()[['date','ngram']].to_json('total_ngram.json')

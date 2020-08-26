from bok_project import multi_processing
from bok_project.ngram.ngram_multi import ngram





# 클래스 선언

if __name__ == "__main__":

    data_dir = r"C:\Users\student\Desktop\newsdata\final_infomax\final_news_infomax_2005_2017.json"
    ng = ngram()
    mp = multi_processing.mp(ng, data_dir=data_dir, save_dir=r'C:\Users\student\Desktop\newsdata\ngrams\\')
    mp.execute(process=4)
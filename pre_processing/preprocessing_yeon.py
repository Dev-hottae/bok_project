import pandas as pd

class Pre_Yeon():

    # 클래스 생성시 파일 위치 인자로 입력
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.data = None

    # 파일 로드
    def load_file(self, file_name):
        self.data = pd.read_json(self.root_dir+file_name)

    # 지정 경로에 파일 새로저장
    def save_file(self, new_name):
        self.data.to_json(self.root_dir + "pre_"+ new_name +'.json')

    # 현재 로드한 파일 랜덤으로 n개 추출보기 (기본값 50)
    def ran_50(self, n=50):
        print(self.data.sample(n=n))

    # 인덱스에 해당하는 데이터 텍스트 전체보기
    def index_search(self, index):
        print(self.data.loc[index, 'text'])

    # 정규표현식 조건에 따라 파일 분할
    def file_divider(self, reg, new_filename):

        # 빈 데이터프레임 생성
        in_condition = pd.DataFrame(data=[],columns=['date','office','text'])
        out_condition = pd.DataFrame(data=[],columns=['date','office','text'])

        # 조건
        if
        self.data['text'] = self.data['text'].str.replace(reg, '')
        self.data['text'] = self.data.text.str.strip()

    # 정규표현식 조건에 맞는 header 부분 잘라내기
    def cut_header(self):

        if self.data.office == '연합인포맥스':
            # 조건에 맞는 데이터 찾기
            reg1 = '^\([가-힣\s]+=[\s가-힣]+\)[\s가-힣]+='
            reg2 = '^\([가-힣\s]+=[\s가-힣]+\)'
            reg3 = '^[\sA-Za-z]+@[A-Za-z.\s]+\(끝\)'

            data50['text'] = data50['text'].str.replace(reg1, '')
            data50['text'] = data50.text.str.strip()

            data50['text'] = data50['text'].str.replace(reg2, '')
            data50['text'] = data50.text.str.strip()

            data50['text'] = data50['text'].str.replace(reg3, '')
            data50['text'] = data50.text.str.strip()

            data50

        if self.data.office == '연합뉴스':
            pass
        if self.data.office == '이데일리':


            pass

    # 정규표현식 조건에 맞는 footer 부분 잘라내기
    def cut_footer(self):
        pass

    # 이외 정규표현식 조건에 맞는 부분 잘라내기
    def cut_else(self):
        pass
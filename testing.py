import pandas as pd

pp = pd.DataFrame(data=[],columns=['date','office','text'])
print(pp)

a = pd.DataFrame(data=[['2020-07-04','ytn','hello my name']], columns=['date','office','text'])
print(a)

pp = pp.append(a)
print(pp)
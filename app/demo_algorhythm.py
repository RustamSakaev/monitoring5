import random
import pickle
from app.Dipoma1 import replaceNone, normScale,CatGroup,getDayAttribute
import pandas as pd

def forecast(df,path_to_model):
    df=pd.DataFrame(df).T

    df = df[["dateofvalue","volume","temperature","pressure"]].copy()
    df['Day']=getDayAttribute(df)
    df = df.drop(['dateofvalue'],axis=1)

    df['volume'] = replaceNone(df['volume'])
    df['temperature'] = replaceNone(df['temperature'])
    df['pressure'] = replaceNone(df['pressure'])

    df['volume'] = df['volume'].fillna('0')
    df['temperature'] = df['temperature'].fillna('0')
    df['pressure'] = df['pressure'].fillna('0')

    df = normScale(df, {'volume', 'temperature', 'pressure'})
    df = CatGroup(df, {'volume', 'temperature', 'pressure'})

    df['volume'] = pd.cut(df['volume'], 10)
    df['volume'] = [int(k.right * 10) for k in df['volume']]
    df['temperature'] = pd.cut(df['temperature'], 10)
    df['temperature'] = [int(k.right * 10) for k in df['temperature']]
    df['pressure'] = pd.cut(df['pressure'], 10)
    df['pressure'] = [int(k.right * 10) for k in df['pressure']]

    loaded_model = pickle.load(open(path_to_model, 'rb'))
    result =loaded_model.predict(df)
    return  result



#for i in range(len(df)):
        #df[i] = str(df[i]).replace(',', '.')


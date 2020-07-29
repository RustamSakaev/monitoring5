# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import random as r
import scipy as sp
import sklearn
import pickle
import re

from sklearn import metrics

from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.model_selection import train_test_split

from sklearn import preprocessing
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import confusion_matrix

def replaceNone(column):
    column=list(column)
    for i in range(len(column)):
        if column[i]=="None":
            column[i]=0
    return column


def normScale(data, columns):
    min_max_scaler = preprocessing.MinMaxScaler()   
    for column in columns: 
        newColumn = data[[column]].values.astype(float)
        normColumn = min_max_scaler.fit_transform(newColumn) 
        data[column] = pd.DataFrame(normColumn) 
    return data

def CatGroup(data, columns):
    for column in columns:
        Dict = pd.Series(data[column].unique()).to_dict()
#inv_map = {v: k for k, v in my_map.items()}
        Dict = {v: k for k,v in Dict.items()}
        data[column] = data[column].map(Dict)
    return data 

#data = pd.read_excel("C:\\Users\\Arrklaid\\Documents\\docs\\csvs\\1601793_try.xlsx",sheet_name=0, header=0)

def getDayAttribute(df):
    Day=[]
    for index, i in df.iterrows():
        newVal = i['dateofvalue']
        if(re.search('8:00|9:00|10:00|11:00|12:00|13:00|14:00|15:00|16:00|17:00|18:00|19:00|20:00|21:00|22:00|23:00', newVal) != None):
            i['Day1'] = 1
        else:
            i['Day1'] = 0
        Day+= [i['Day1']]
    return Day



def learn(data):

    data['Day']=getDayAttribute(data)

    '''для каждой строки
        если нет тру класса:           
            закинуть айди аварии в тру класс    
        '''

    y = data['true_class']
    name=list(data['label'])[0]
    if name!='nan':

        data=data[['volume','pressure','temperature','Day']].copy()

        data['volume']=replaceNone(data['volume'])
        data['temperature'] = replaceNone(data['temperature'])
        data['pressure'] = replaceNone(data['pressure'])

        #замена null
        data['volume'] = data['volume'].fillna('0')
        data['temperature'] = data['temperature'].fillna('0')
        data['pressure'] = data['pressure'].fillna('0')

        #нормазлизуем данные
        data = normScale(data,{'volume','temperature','pressure'})
        data = CatGroup(data, {'volume','temperature','pressure'})

        data['volume'] = pd.cut(data['volume'],10)
        data['volume'] = [int(k.right*10) for k in data['volume']]
        data['temperature'] = pd.cut(data['temperature'],10)
        data['temperature'] = [int(k.right*10) for k in data['temperature']]
        data['pressure'] = pd.cut(data['pressure'],10)
        data['pressure'] = [int(k.right*10) for k in data['pressure']]

        x_train, x_test, y_train, y_test = train_test_split(data, y, train_size=0.99,random_state= 30)

        #DecisionTreeClassifier
        clf = DecisionTreeClassifier(criterion='entropy')
        clf.fit(x_train,y_train)
        filename = 'app/classificators/'+str(name) + '.sav'
        pickle.dump(clf, open(filename, 'wb'))
        print("done",name)
from app.main import bp
from flask import render_template
from flask_login import login_required
import pandas as pd
import json
import re
from app.models import Device, Indication, Pipe
from app import db
from flask import request, json, jsonify

@bp.route('/base', methods=['GET','POST'])
@login_required
def base():
    #получение показаний прибора
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)
        data = data.replace('{', '').replace('}', '').replace('"', '')
        id = data.split(':')[1].strip()
        device = Device.query.filter(Device.id==id).first()
        indications = Indication.query.filter(Indication.device_id==device.id).all()
        inds=[]
        for i in indications:
            inds+=[i.as_dict()]

    return json.dumps(inds)

@bp.route('/remove', methods=['GET','POST'])
@login_required
def remove():
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data, ensure_ascii=False)
        data = data.replace('{', '').replace('}', '').replace('"', '')
        data = data.split(',')
        if data[1].split(':')[1].strip() == 'pipe':
            id=data[0].split(':')[1].strip()
            pipe = Pipe.query.filter(Pipe.id == id).delete()
            db.session.commit()
        else:
            address = data[0].split(':')[1].strip()
            device = Device.query.filter(Device.address_raw == address).delete()
            db.session.commit()
    return "SUCCESS"

@bp.route('/pipes', methods=['GET','POST'])
@login_required
def pipes():
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)
        data = data.split('",')
        for i in range(len(data)):
            data[i] = data[i].replace('{', '').replace('}', '').replace('"', '').replace('\\','')
            data[i] = data[i].split(':')
            if len(data[i]) == 3:
                data[i].remove(" ")
        coords=[]
        for row in data:
            coords += [row[1].split(',')]

        for i in range(len(coords)):
            for j in range(len(coords[i])):
                coords[i][j] = float(coords[i][j])

        coords = str(coords)
        pipe=Pipe(coordinates=coords)
        db.session.add(pipe)
        db.session.commit()
        print(coords)
    return "Success"

@bp.route('/coordinates', methods=['GET','POST'])
@login_required
def coordinates():
    #заполнение приборов координатами
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)
        data = data.split('",')
        for i in range(len(data)):
            data[i] = data[i].replace('{', '').replace('}', '').replace('"', '').replace('\\','')
            data[i] = data[i].split(':')
            if len(data[i]) == 3:
                data[i].remove(" ")
        for row in data:
            address=row[0]
            print(address)
            device = Device.query.filter(Device.address_clean==address).first()
            device.coordinates=row[1]
            db.session.commit()
        print(len(data))

    return "True"

@bp.route('/update_coordinates',methods=['GET','POST'])
@login_required
def update_coordinates():
    #обновление координат прибора
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)
        data = data.replace('{', '').replace('}', '').replace('"', '')
        data = data.split(',')
        if data[2].split(':')[1].strip()=='Device':            
            id = data[1].split(':')[1].strip()
            coordinates = data[0].replace(';', ',').split(':')[1].strip()
            device = Device.query.filter(Device.id==id).first()
            device.coordinates=coordinates
            db.session.commit()
        else:
            id=data[1].split(':')[1].strip()
            coordinates = data[0].replace(';', ',').split(':')[1].strip()
            pipe = Pipe.query.filter(Pipe.id == id).first()
            pipe.coordinates = coordinates
            db.session.commit()
    return "success"

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    #формирование чистых адресов и заполнение БД
    """def valid_index(df):
        df.index = range(len(df))

    p = pd.read_csv('app/static/Pribor.csv', sep=';')
    p = p['НазваниеПрибора']   
    p[811] = str(p[811]).replace('(30 лет Победы 109)', '')
    for i in range(len(p)):
        p[i] = p[i].lower()

    x = re.compile('(\(ук.*)|(тв7)|(ввод\d)|(подвал\s\d)|(ввод.*)|(ук)|(перешит)|(тепло тюмени)|(гвс)|(3х трубка)')
    x1 = re.compile('(\d+-го)|(\d+ой)')
    x2 = re.compile('(\d+\sлет)')

    for i in range(len(p)):
        p[i] = re.sub(x, '', str(p[i]))
        p[i] = re.sub(x1, '', str(p[i]))
        p[i] = re.sub(x2, 'лет', str(p[i]))
        p[i] = p[i].replace('9 мая', 'мая').replace('9 января', 'января')
        p[i] = str(p[i]).strip()
        #tmp_device = Device.query.filter(Device.address_raw==p_raw[i]).first()
        #tmp_device.address_clean=p[i]
        #db.session.commit()"""
    #чистые адреса для тех приборов, для которых скрипт выше почему-то не сработал
    """ids = [832,983,1230,1253,1287,1327]
    values = ['садовая 113а','мельничная 5','тсрв-026м_1213458_21-01-2018','тсрв-026м_1301643_09-04-2018','тсрв-026м_1206930_30-04-2018','тсрв-026м_1305247_28-07-2018']
    x=0
    for i in ids:
        device = Device.query.get(i)
        device.address_clean=values[x]
        x+=1
        db.session.commit()"""

    #приборы без координат, которые отправляются в геокодер
    """devices = Device.query.filter(Device.coordinates == None).all()
    dvcs = []
    for i in devices:
        dvcs += [i.as_dict()]
    dvcs=pd.DataFrame(dvcs)
    dvcs = json.dumps(dvcs, ensure_ascii=False)
    dvcs.to_csv('devices.csv', index=False, sep=";", encoding='windows-1251')"""

    #отбор приборов для вывода на карту
    devices = Device.query.filter(Device.coordinates != None).all()
    devices = devices[:50]

    #devices = Device.query.filter(Device.address_raw=="тест").all()

    pipes=Pipe.query.all()



    return render_template('index.html', title='Система мониторинга',devices=devices,pipes=pipes)


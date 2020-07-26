from app.main import bp
from flask import render_template
from flask_login import login_required
import pandas as pd
import json
import re
from app.models import Device, Indication, Pipe, District
from app import db
from flask import request, json, jsonify, send_file,send_from_directory,Response
import datetime
from datetime import timedelta
from pathlib import Path
import math
import ast
import io
from docxtpl import DocxTemplate


@bp.route('/set_true_class', methods=['GET','POST'])
@login_required
def set_class():
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)
        data=ast.literal_eval(data)
        id=int(data['id'])
        true_id=data['true_id']
        ind = Indication.query.filter(Indication.id==id).first()
        if true_id=='NULL':
            ind.true_class=None
        else:
            ind.true_class=int(true_id)
        db.session.commit()
    return "Success"


@bp.route('/base', methods=['GET','POST'])
@login_required
def base_period():
    #получение показаний прибора
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)

        data=ast.literal_eval(data)
        print(data)
        print(len(data))

        old_max_date=""
        id = data["id"]
        is_first_load = data["is_first_load"]
        old_max_id = data["max_id"]
        period = data["period"]

        if len(data)>4:
            old_max_date = data["max_date"]
        print(old_max_date)
        #now=datetime.datetime.now()
        now = datetime.datetime(2020, 5, 4, 19, 00)
        today72=now
        indications=[]
        if period=="6hour":
                today72 = now - datetime.timedelta(hours=6)
        elif period=="12hour":
            today72 = now - datetime.timedelta(hours=12)
        elif period=="24hour":
            today72 = now - datetime.timedelta(days=1)
        elif period=="3day":
            today72 = now - datetime.timedelta(days=3)
        elif period=="7day":
            today72 = now - datetime.timedelta(days=7)
        if is_first_load=='true':
            if period!="all":
                indications = Indication.query.filter(Indication.device_id == id).filter(
                    Indication.dateofvalue >= today72).order_by(Indication.dateofvalue.desc()).all()
            else:
                indications = Indication.query.filter(Indication.device_id == id).order_by(
                    Indication.dateofvalue.desc()).all()
        else:
            if old_max_id == "":
                if period != "all":
                    indications = Indication.query.filter(Indication.device_id == id).filter(
                        Indication.dateofvalue >= today72).order_by(Indication.dateofvalue.desc()).all()
                else:
                    indications = Indication.query.filter(Indication.device_id == id).order_by(
                        Indication.dateofvalue.desc()).all()
            else:
                max_id = db.session.query(db.func.max(Indication.id)).filter(Indication.device_id == id).scalar()
                print("old id {0}",old_max_id)
                print("new id {0}",max_id)
                print("device id {0}",id)
                print("period {0}",period)


                if old_max_date!="":
                    x = re.compile('GMT.*')
                    old_max_date = re.sub(x, '', old_max_date)
                    old_max_date = datetime.datetime.strptime(old_max_date, "%a %b %d %Y %H:%M:%S ")
                    max_date = db.session.query(db.func.max(Indication.updated_at)).filter(Indication.device_id == id).scalar()
                    if int(max_id) > int(old_max_id) or max_date>old_max_date:
                        if period != "all":
                            indications = Indication.query.filter(Indication.device_id == id).filter(
                                Indication.dateofvalue >= today72).order_by(Indication.dateofvalue.desc()).all()
                        else:
                            indications = Indication.query.filter(Indication.device_id == id).order_by(
                                Indication.dateofvalue.desc()).all()
                else:
                    if int(max_id) > int(old_max_id):
                        if period != "all":
                            indications = Indication.query.filter(Indication.device_id == id).filter(
                                Indication.dateofvalue >= today72).order_by(Indication.dateofvalue.desc()).all()
                        else:
                            indications = Indication.query.filter(Indication.device_id == id).order_by(
                                Indication.dateofvalue.desc()).all()


        inds=[]
        for i in indications:
          inds+=[i.as_dict()]
        print(len(inds))
    return json.dumps(inds)



"""@bp.route('/base', methods=['GET','POST'])
@login_required
def base():
    #получение показаний прибора
    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)
        data = data.replace('{', '').replace('}', '').replace('"', '')
        id = data.split(':')[1].strip()
        device = Device.query.filter(Device.id==id).first()
        indications = Indication.query.filter(Indication.device_id==device.id).order_by(Indication.dateofvalue.desc()).all()
        inds=[]
        for i in indications:
            inds+=[i.as_dict()]

    return json.dumps(inds)"""

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
            pipe = Pipe.query.filter(Pipe.id == id).first()
            pipe.deleted=True
            db.session.commit()
        else:
            address = data[0].split(':')[1].strip()
            device = Device.query.filter(Device.address == address).first()
            device.deleted=True
            db.session.commit()
    return "SUCCESS"

#добавление трубы
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
    return "Success"
#получить новые аварии
def getlastincidents():

    today = datetime.datetime.now().replace(second=0, microsecond=0)
    today72 = today - datetime.timedelta(days=3)
    #incidents = Indication.query.filter(Indication.dateofvalue >= today72).all() #показания за последние 3 дня
    incidents = Indication.query.all()

    incd = []
    for i in incidents:
        incd += [i.as_dict()]
    incd = pd.DataFrame(incd)


    devices = list(set(incd['device_id']))
    act_devices = []
    for i in range(len(devices)):
        result = incd[incd.device_id == devices[i]].sort_values(by=['dateofvalue'], ascending=False).iloc[0]["class_of_incident_id"]
        if result != "None" and result!="5":
            act_devices += [devices[i]]

    tmp = []
    ovrl = []

    for i in range(len(act_devices)):
        tmp += [incd[incd.device_id == act_devices[i]].sort_values(by=['dateofvalue'], ascending=False).iloc[0:2]]

    for df in tmp:
        df['new'] = 'False'
        tmp_inc = df['class_of_incident_id']
        if len(tmp_inc)!=1:
            if tmp_inc.iloc[1] == "None" or tmp_inc.iloc[1] == "2":
                df['new'].iloc[0] = 'True'
        else:
            df['new'].iloc[0] = 'True'
        ovrl += [df.iloc[0]]

    ovrl = pd.DataFrame(ovrl)
    if len(ovrl)!=0:
        ovrl=ovrl.sort_values(by=['new','dateofvalue'],ascending=False)
    return ovrl

#заполнение csv нужными временами
def change_csv(year,month,day,hour,minute,path,delta):
    out = pd.read_csv('app/static/data/'+path+'.csv', sep=';')
    time0 = datetime.datetime(year, month, day, hour, minute)
    init_dates=out["ДатаВремя"]
    new_dates = init_dates.copy()
    new_dates[0] = time0
    for i in range(len(new_dates)):
        if i == 0:
            continue
        new_dates[i] = new_dates[i - 1] + timedelta(minutes=delta)
    out["ДатаВремя"] = new_dates
    out.to_csv('app/static/data/'+path+'_1.csv', sep=";",index=False, encoding='windows-1251')

def write_csv_into_db():
    Devices = Device.query.filter(Device.label != 'nan').all()
    dvcs = []
    for i in Devices:
        dvcs += [i.as_dict()]
    dvcs = pd.DataFrame(dvcs)

    labels = {}
    for i in range(len(dvcs)):
        labels[dvcs["id"].loc[i]] = dvcs["label"].loc[i]
    # {device_id:label}

    for id, label in labels.items():
        tmp_path = Path("app/static/data/" + label + '_1.csv')
        print(tmp_path.exists())
        if tmp_path.exists():
            tmp = pd.read_csv('app/static/data/' + label + '_1.csv', sep=';', encoding='windows-1251')
            tmp = tmp[:50]
            values = tmp[["ДатаВремя", "P3", "V3", "t3"]].copy()
            for key, row in values.iterrows():
                p3 = float(str(row["P3"]).replace(',', '.'))
                v3 = float(str(row["V3"]).replace(',', '.'))
                t3 = float(str(row["t3"]).replace(',', '.'))
                if math.isnan(p3):
                    p3=None
                if math.isnan(v3):
                    v3=None
                if math.isnan(t3):
                    t3=None
                date = row["ДатаВремя"]
                ind = Indication(dateofvalue=date,device_id=id,deleted=False,pressure=p3,temperature=t3, volume=v3)
                db.session.add(ind)
                db.session.commit()
    return "SUCCESS"


@bp.route('/new_incidents',methods=['GET','POST'])
@login_required
def incidents():
    x = re.compile('GMT.*')
    incidents=[]

    if request.method == 'POST':
        data = request.form
        data = json.dumps(data,ensure_ascii=False)
        data=ast.literal_eval(data)
        max_date=data["max_date"]
        rows = data["rows"]

        max_date = re.sub(x, '', max_date)
        max_date= datetime.datetime.strptime(max_date, "%a %b %d %Y %H:%M:%S ")
        new_max_date = db.session.query(db.func.max(Indication.updated_at)).scalar()


        if new_max_date > max_date:
            incidents = getlastincidents()
            incidents['max_updated_at'] = str(new_max_date)
            incidents = incidents.to_json(orient='records')
        else:
            rows = ast.literal_eval(rows)
            r = pd.DataFrame(rows.items())
            rows = tuple(rows)

            indications = Indication.query.filter(Indication.id.in_(rows)).all()

            inds = []
            for i in indications:
                inds += [i.as_dict()]
            inds = pd.DataFrame(inds)
            inds = inds[['id', 'true_class']]

            true_site=list(r[1])
            true_db=list(inds['true_class'])

            needupdate=False

            for i in range(len(true_site)):
                    if true_site[i]!=true_db[i]:
                        needupdate=True
            print(true_site)
            print(true_db)
            print(needupdate)
            #inds=inds.set_index('id').T.to_dict('list')
            #incidents = {"need_update":str(needupdate),"true_class":inds}
            #incidents = json.dumps(incidents)
            inc = getlastincidents()
            inc = inc.to_json(orient='records')
            incidents = {"need_update": str(needupdate), "data": inc}
    return incidents


@bp.route('/export',methods=['GET','POST'])
@login_required
def export():
    print('hello')
    districts = request.form.getlist('select')
    start = request.form.getlist('trip-start')
    end = request.form.getlist('trip-end')
    incident=request.form.getlist('type')

    additional=""
    if len(districts)!=0:
        if districts[0] != '':
            for i in range(len(districts)):
                districts[i] = int(districts[i])
            if len(districts)>1:
                districts=tuple(districts)
                additional+=" and district.id IN "+str(districts)
            else:
                additional += " and district.id =" + str(districts[0])

    if incident[0]!='' and incident[0]!='all':
        incident[0] = int(incident[0])
        additional += " and class_of_incident.id =" + str(incident[0])
    if incident[0]=='all':
        additional += " and class_of_incident.id !=5"

    if start[0]!='':
        start[0]=datetime.datetime.strptime(start[0], '%Y-%m-%d').strftime('%Y-%d-%m')
        additional += " and indication.dateofvalue >='" + str(start[0])+"'"

    if end[0]!='':
        end[0]=datetime.datetime.strptime(end[0], '%Y-%m-%d').strftime('%Y-%d-%m')
        additional += " and indication.dateofvalue <='" + str(end[0])+"'"

    current_date = datetime.datetime.today()
    current_date = current_date.strftime("%d.%m.%Y")

    query = db.engine.execute('''
                select district.name, class_of_incident.name, count(indication.id)
                from class_of_incident, indication, device,district
                where indication.class_of_incident_id=class_of_incident.id 
                    and indication.device_id=device.id 
                    and device.district_id=district.id '''+additional+''' 
                group by district.name,class_of_incident.name
                order by count(indication.id) DESC''')
    query=pd.DataFrame(query)
    print(query)
    doc = DocxTemplate("app/export_templates/test_report.docx")

    if end[0]=='':
        end[0]=current_date
    else:
        end[0] = datetime.datetime.strptime(end[0], '%Y-%d-%m').strftime('%d.%m.%Y')
    if start[0]=='':
        start[0]='01.01.1970'
    else:
        start[0] = datetime.datetime.strptime(start[0], '%Y-%d-%m').strftime('%d.%m.%Y')

    context = {'current_date': current_date, 'start': start[0], 'end': end[0],
               'col_labels': ['Район', 'Тип нештатной ситуации', 'Кол-во'], 'tbl_contents': []}

    x=1
    count=0
    for index, row in query.iterrows():
        context['tbl_contents']+=[{'label': x, 'cols':[row[0],row[1],row[2]]}]
        count+=int(row[2])
        x+=1

    context['count']=count
    doc.render(context)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    return send_file(file_stream, as_attachment=True, attachment_filename='report.doc')
    

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    #fillWord()
    #формирование чистых адресов и заполнение БД
    def valid_index(df):
        df.index = range(len(df))

    #write_csv_into_db()
    """p = pd.read_csv('app/static/Pribor.csv', sep=';')
    for i in range(len(p)):
        address = p["НазваниеПрибора"].loc[i]
        label = str(p["Метка"].loc[i]).replace('.0','')
        tmp=Device.query.filter(Device.address_raw==address).first()
        tmp.label=label
        db.session.commit()"""


    """p[811] = str(p[811]).replace('(30 лет Победы 109)', '')
    for i in range(len(p)):
        p[i] = p[i].lower()"""

    """p = pd.read_csv('app/static/Pribor.csv', sep=';')
    p = p["НазваниеПрибора"].copy()
    p_raw = p["НазваниеПрибора"].copy()

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
        tmp_device = Device.query.filter(Device.address_raw==p_raw[i]).first()
        tmp_device.address_clean=p[i]
        db.session.commit()"""

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
    devices = Device.query.all()
    devices=devices[:50]
    dvcs = []
    for i in devices:
        dvcs += [i.as_dict()]
    #dvcs=pd.DataFrame(dvcs)
    dvcs = json.dumps(dvcs, ensure_ascii=False)
    #dvcs.to_csv('devices.csv', index=False, sep=";", encoding='windows-1251')

    #отбор приборов для вывода на карту
    devices = Device.query.filter(Device.coordinates != None).all()

    #devices = devices[:605]

    #devices = Device.query.filter(Device.address_raw=="тест").all()

    pipes=Pipe.query.filter(Pipe.deleted==None).all()

    #change_csv(2020,6,10,7,0,'1307423',60)
    #tmp = pd.read_csv('app/static/data/1601793_1.csv', sep=';',encoding='windows-1251')

    """now = datetime.datetime(2020, 5, 4, 22, 45)
    indctn = Indication(dateofvalue=str(now),value=1,device_id=6)
    db.session.add(indctn)
    db.session.commit()
    print('data is written')"""

    """dist = pd.read_csv('app/static/districts.csv', sep=';', encoding='windows-1251')
    for i in range(len(dist)):
        name=dist['Name'].loc[i]
        coordinates=dist['Coordinates'].loc[i]
        d = District(name=name,coordinates=coordinates)
        db.session.add(d)
        db.session.commit()"""
    districts = District.query.all()

    """dist = pd.read_csv('devices1.csv', sep=';', encoding='windows-1251')
    for i in range(len(dist)):
        id=int(dist["id"].iloc[i])
        district =dist["district_id"].iloc[i]
        if district!="None":
            district=int(district)
            dev = Device.query.filter(Device.id == id).first()
            dev.district_id = district
            db.session.commit()"""
    
    incidents=getlastincidents()
    max_updated_at=db.session.query(db.func.max(Indication.updated_at)).scalar()
    max_updated_at=str(max_updated_at)



    """device = Device.query.filter(Device.coordinates == None).all()
    dvcs = []
    for i in device:
        dvcs += [i.as_dict()]
    dvcs = pd.DataFrame(dvcs)
    dvcs=dvcs['id']
    print(dvcs)
    for row in dvcs:
        d=Device.query.filter(Device.id==row).first()
        d.deleted=True
        db.session.commit()"""
    return render_template('index.html', title='Система мониторинга',devices=devices,dvcs=dvcs,pipes=pipes,districts=districts,incidents=incidents,max_updated_at=max_updated_at)


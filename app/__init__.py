from flask import Flask
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import atexit
import pandas as pd
import os.path
from pathlib import Path
import math
from threading import Thread
import threading
import time

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login = LoginManager()
max_id_global=None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bootstrap.init_app(app)
    login.init_app(app)
    login.login_view = 'auth.login'
    login.login_message = "Войдите, чтобы увидеть эту страницу"
    db.init_app(app)
    migrate.init_app(app, db)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.models import User, Device, Indication
    from app.demo_algorhythm import forecast
    from app.Dipoma1 import learn

    with app.app_context():
        max_id_global = db.session.query(db.func.max(Indication.id)).scalar()

    print('initial')
    print(max_id_global)



    def get_forecast(row):
        print("current thread {0} ",threading.current_thread().ident)
        id = row["id"]
        device = row['device_id']
        with app.app_context():
            path_to_model = db.session.query(Device.path_to_model).filter(Device.id == device).scalar()
            results = forecast(row, path_to_model)
            print('res')
            print(results)
            res = results[0]
            tmp_ind = Indication.query.filter(Indication.id == id).first()
            tmp_ind.class_of_incident_id = int(res)+1
            tmp_ind.updated_at = datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')
            db.session.commit()


    def check_max_id(max_id):
        global max_id_global

        with app.app_context():

            new_max_id = db.session.query(db.func.max(Indication.id)).scalar()
            if new_max_id > max_id:
                indications = Indication.query.filter(Indication.id > max_id)
                max_id_global = new_max_id

                scheduler.modify_job(task2.id, args=[max_id_global])
                indc = []
                for i in indications:
                    indc += [i.as_dict()]
                incd = pd.DataFrame(indc)
                ids = incd['id']
                i = 0

                start = time.time()
                threads = []
                for key,row in incd.iterrows():
                    threads.append(Thread(target=get_forecast, args=([row])))
                    threads[i].start()
                    i += 1
                    """id=row["id"]
                    device=row['device_id']
                    path_to_model=db.session.query(Device.path_to_model).filter(Device.id == device).scalar()
                    results = forecast(row,path_to_model)
                    res=results[0]
                    tmp_ind=Indication.query.filter(Indication.id==id).first()
                    tmp_ind.class_of_incident_id=(int(res)+1)
                    tmp_ind.updated_at=str(datetime.datetime.now()).strftime('%Y-%d-%m %H:%M:%S')
                    db.session.commit()"""
                for t in threads:
                    t.join()
                end = time.time()
                print(end - start)
            else:
                print('not changed')

            print('вход {0}',max_id)
            print('выход {0}', max_id_global)
        return "Success"

    def relearn():
        with app.app_context():
            Devices = Device.query.all()
            dvcs = []
            for i in Devices:
                dvcs += [i.as_dict()]
            dvcs = pd.DataFrame(dvcs)
            dvcs=list(dvcs['id'])
            for dvc in dvcs:
                Indications = Indication.query.filter(Indication.device_id==dvc)
                indc = []
                for i in Indications:
                    indc += [i.as_dict()]
                indc = pd.DataFrame(indc)
                if len(indc)>10:
                    learn(indc)



    def check_csv():
        with app.app_context():
            Devices = Device.query.filter(Device.label != 'nan').all()
        dvcs = []
        for i in Devices:
            dvcs += [i.as_dict()]
        dvcs = pd.DataFrame(dvcs)

        labels = {}
        for i in range(len(dvcs)):
            labels[dvcs["id"].loc[i]] = dvcs["label"].loc[i]
        # {device_id:label}

        now = datetime.datetime.now().replace(second=0, microsecond=0)
        for id, label in labels.items():
            tmp_path = Path("app/static/data/"+label+'_1.csv')
            if tmp_path.exists():
                tmp = pd.read_csv('app/static/data/' + label + '_1.csv', sep=';',encoding='windows-1251')
                times = tmp["ДатаВремя"].copy()
                for z in range(len(times)):
                    times[z] = datetime.datetime.strptime(times[z], '%Y-%m-%d %H:%M:%S')
                    #times[z] = datetime.datetime.strptime(times[z], '%d.%m.%Y %H:%M')

                    diff = now - times[z]
                    if diff.seconds / 60 < 60 and diff.days == 0:
                        t3 = float(str(tmp["t3"].loc[z]).replace(',','.'))
                        v3 = float(str(tmp["V3"].loc[z]).replace(',', '.'))
                        p3 = float(str(tmp["P3"].loc[z]).replace(',', '.'))
                        if math.isnan(p3):
                            p3 = None
                        if math.isnan(v3):
                            v3 = None
                        if math.isnan(t3):
                            t3 = None
                        print('p3={0} v3={1} p3={2}',p3,v3,t3)
                        with app.app_context():
                            oldind = Indication.query.filter(Indication.device_id==id).all()
                            inds = []
                            for i in oldind:
                                inds += [i.as_dict()]
                            inds = pd.DataFrame(inds)
                            last_time = inds['dateofvalue']
                            last_time=last_time[len(last_time) - 1]
                            last_time=datetime.datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')

                            if times[z]!=last_time:
                                print("old time {0}",last_time)
                                print("new time {0}",str(times[z]))
                                times[z]=str(times[z].strftime('%Y-%d-%m %H:%M:%S'))
                                indctn = Indication(dateofvalue=str(times[z]),deleted=False,pressure=p3,temperature=t3,volume=v3,device_id=id)
                                db.session.add(indctn)
                                db.session.commit()
                                break
                            else:
                                print('write anything')
        return "Success"

    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        #scheduler.add_job(func=check_csv, trigger="interval", seconds=20)
        #task2 = scheduler.add_job(func=check_max_id, trigger="interval",args=[max_id_global], seconds=20)
        #relearn_task = scheduler.add_job(func=relearn, trigger="cron", hour='0')
        #relearn_task = scheduler.add_job(func=relearn, trigger="interval", seconds=10)
        scheduler.start()


    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/monitoring.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Monitoring startup')
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        atexit.register(lambda: scheduler.shutdown())


    return app

from app import models
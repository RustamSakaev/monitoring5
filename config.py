import os
from dotenv import load_dotenv
import urllib
import pyodbc
import sqlalchemy as sa


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


#params = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-S2U77HG;DATABASE=Diploma;UID=monitoring_user;PWD=123')
#engine = sa.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yareyaredaze'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3DDESKTOP-S2U77HG%3BDATABASE%3DDiploma%3BTrusted_Connection%3Dyes%3B'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3DDESKTOP-S2U77HG%3BDATABASE%3DDiploma%3BUID%3Dmonitoring_user%3BPWD%3D123'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
   # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
   #                           'sqlite:///' + os.path.join(basedir, 'app.db')

import random,string,os,time,requests,json,csv,re,sys,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from dotenv import load_dotenv
from closeio_api import Client

basedir = os.path.join(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
proxy_file = os.path.join(basedir, 'proxies.txt')
leads_file = os.path.join(basedir, 'leads.json')
img_path = os.path.join(basedir,'assets/images')
logo = os.path.join(img_path,'logo.ico')
start_img_file = os.path.join(img_path,'start.png')
stop_img_file = os.path.join(img_path,'stop.png')

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "Esmex 1.0"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

from utils import load_proxies
proxies = load_proxies()

state = {'ON':False}


load_dotenv(env_path)
api_key = os.getenv('APIKEY')
api = Client(api_key)


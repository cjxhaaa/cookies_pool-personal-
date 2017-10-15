import time
from multiprocessing import Process
from config import *
from api import app
from generator import *

db=3

class Scheduler(object):
    @staticmethod
    def generate_cookie(cycle=1):
        while True:
            print('Generating Cookies')
            try:
                for name, cls in { 'weibo': 'CookiesGenerator'}.items():
                    generator = eval(cls + '(name="' + name + '",db='+str(REDIS_DB)+')')
                    generator.run()
                    print('Generator Finished')
                    time.sleep(5)
            except Exception as e:
                print(e.args)

    @staticmethod
    def api():
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        if GENERATOR_PROCESS:
            generate_process = Process(target=Scheduler.generate_cookie)
            generate_process.start()

        if API_PROCESS:
            api_process = Process(target=Scheduler.api)
            api_process.start()
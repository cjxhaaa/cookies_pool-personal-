import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from redis_db import AccountRedisClient


DEFAULT_BROWSER = 'Chrome'

class CookiesGenerator(object):
    def __init__(self,name='default',browser_type = DEFAULT_BROWSER,db=0):
        '''
        初始化浏览器对象
        :param name: 名称
        :param browser_type: 默认浏览器为Chrome
        '''
        self.name = name
        self.account_db = AccountRedisClient(name=self.name,db=db)
        self.browser_type = browser_type

    def _browser(self,browser_type):
        '''
        通过browser_type判断使用的浏览器
        :param browser_type: 
        :return: 
        '''
        if browser_type == 'PhantomJS':
            dcap = webdriver.DesiredCapabilities.PHANTOMJS
            headers = {'Accept': '*/*',
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'en-US,en;q=0.8',
                       'Cache-Control': 'max-age=0',
                       }
            for key,value in enumerate(headers):
                capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
                dcap[capability_key] = value
            dcap['phantomjs.page.settings.userAgent'] = ''
            self.browser = webdriver.PhantomJS(desired_capabilities=dcap)
            self.browser.set_window_size(1400,1000)
        elif browser_type == 'Chrome':
            self.browser == webdriver.Chrome()

    def get_account(self):
        '''
        从数据库获取账户密码
        :return: 
        '''
        accounts = self.account_db.all()
        accounts = list(accounts)
        print(accounts)

    def _get_cookies(self,username,password):
        print('Generating Cookies of ',username)
        # self.browser.get('http://my.sina.com.cn/profile/unlogin')
        self.browser.get('https://login.sina.com.cn/signup/signin.php')
        wait = WebDriverWait(self.browser,20)
        try:
            login = wait.until()



if __name__ == '__main__':
    generator = CookiesGenerator(name='weibo',db=3)
    generator.get_account()
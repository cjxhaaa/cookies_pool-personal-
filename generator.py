import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,WebDriverException
from redis_db import AccountRedisClient
from PIL import Image


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
            self.browser = webdriver.Chrome()

    def get_account(self):
        '''
        从数据库获取账户密码
        :return: 
        '''
        accounts = self.account_db.all()
        accounts = list(accounts)
        print(accounts)

    def _get_cookie(self,username):
        wait = WebDriverWait(self.browser,5)
        success = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'me_portrait_w')))
        if success:
            print('登陆成功')
            self.browser.get('http://weibo.cn/')
            if '我的首页' in self.browser.title:
                c = self.browser.get_cookies()
                print(c)
                cookies = {}
                for cookie in c:
                    cookies[cookie['name']] = cookie['value']
                print(cookies)
                print('成功获取到Cookies')
                return (username, json.dumps(cookies))


    def get_cookies(self,username,password):
        print('Generating Cookies of ',username)
        # self.browser.get('http://my.sina.com.cn/profile/unlogin')
        self.browser.delete_all_cookies()
        self.browser.get('https://login.sina.com.cn/signup/signin.php')
        try:
            self.browser.find_element_by_xpath('//*[@id="username"]').clear()
            self.browser.find_element_by_xpath('//*[@id="username"]').send_keys(username)
            self.browser.find_element_by_xpath('//*[@id="password"]').clear()
            self.browser.find_element_by_xpath('//*[@id="password"]').send_keys(password)
            self.browser.find_element_by_xpath('//*[@id="vForm"]/div[2]/div/ul/li[7]/div[1]/input').click()
            try:
                result = self._get_cookie(username)
                if result:
                    return result
            except TimeoutException:
                print('出现验证码，开始识别')
                img_url = self.browser.find_element_by_xpath('//*[@id="check_img"]').get_attribute('src')
                img_cookies = self.browser.get_cookies()
                cookies_dict = {}
                for cookie in img_cookies:
                    cookies_dict[cookie['name']] = cookie['value']
                print(cookies_dict)
                r = requests.get(img_url,cookies=cookies_dict)
                with open(username+'.png','wb') as p:
                    p.write(r.content)
                # image = Image.open(username+'.png')
                # image.show()
                t = input('请输入验证码：')
                self.browser.find_element_by_xpath('//*[@id="door"]').send_keys(t)
                self.browser.find_element_by_xpath('//*[@id="vForm"]/div[2]/div/ul/li[7]/div[1]/input').click()
                result = self._get_cookie(username)
                if result:
                    return result
        except WebDriverException as e:
            print(e.args)






if __name__ == '__main__':
    generator = CookiesGenerator(name='weibo',db=3)
    generator._browser('Chrome')
    generator.get_cookies('15173492987','688458ps')
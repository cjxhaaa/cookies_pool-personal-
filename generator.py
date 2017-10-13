import json
import requests
import os,time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,WebDriverException
from redis_db import AccountRedisClient,CookiesRedisClient
from PIL import Image


DEFAULT_BROWSER = 'Chrome'

class CookiesGenerator(object):
    def __init__(self,name='default',browser_type=DEFAULT_BROWSER,db=0):
        '''
        初始化浏览器对象
        :param name: 名称
        :param browser_type: 默认浏览器为Chrome
        '''
        self.name = name
        self.account_db = AccountRedisClient(name=self.name,db=db)
        self.cookies_db = CookiesRedisClient(name=self.name,db=db)
        self.browser_type = browser_type

    def _browser(self):
        '''
        通过browser_type判断使用的浏览器
        :param browser_type: 
        :return: 
        '''
        if self.browser_type == 'PhantomJS':
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
        elif self.browser_type == 'Chrome':
            self.browser = webdriver.Chrome()

    def _get_cookie(self,username):
        '''
        登陆后获取cookies
        :param username: 
        :return: 
        '''
        wait = WebDriverWait(self.browser,5)
        success = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'me_portrait_w')))
        if success:
            print('登陆成功')
            self.browser.get('http://weibo.cn/')
            if '我的首页' in self.browser.title:
                c = self.browser.get_cookies()
                cookies = {}
                for cookie in c:
                    cookies[cookie['name']] = cookie['value']
                print(cookies)
                print('成功获取到Cookies')
                self.browser.close()
                del self.browser
                return (username, json.dumps(cookies))

    def _yzm(self,username):
        '''
        验证码验证部分
        :param username: 
        :return: 
        '''
        yzm = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/ul/li[4]/img')))
        yzm_url = yzm.get_attribute('src')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        r = requests.get(yzm_url, cookies=self.cookies_dict, headers=headers)
        img_name = '验证码/' + username + '.png'
        with open(img_name, 'wb') as p:
            p.write(r.content)
        login_status = self.browser.find_element_by_xpath('/html/body/div[6]/div[2]/p')
        print('登录状态：' + login_status.text)
        t = input('请输入验证码，输入next跳过此账号：')
        if  t == 'next':
            print('next')
            return
        self.browser.find_element_by_xpath('/html/body/div[6]/div[2]/ul/li[4]/input').send_keys(t)
        if os.path.exists(img_name):
            os.remove(img_name)
        submit = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/ul/li[6]/span/a')))
        submit.click()
        try:
            result = self._get_cookie(username)
            if result:
                return result
        except:
            print('登陆失败')
            return self._yzm(username)

    def get_cookies(self,username,password):
        '''
        登陆操作部分
        :param username: 
        :param password: 
        :return: 
        '''
        self._browser()
        print('Generating Cookies of ',username)
        # self.browser.get('http://my.sina.com.cn/profile/unlogin')
        # self.browser.delete_all_cookies()
        # time.sleep(1)
        self.browser.get('http://my.sina.com.cn/profile/unlogin')
        self.wait = WebDriverWait(self.browser,20)
        try:
            login = self.wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="hd_login"]')))
            login.click()
            user = self.wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[6]/div[2]/ul/li[2]/input')))
            user.send_keys(username)
            psd = self.wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[6]/div[2]/ul/li[3]/input')))
            psd.send_keys(password)
            submit = self.wait.until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[6]/div[2]/ul/li[6]/span/a')))
            submit.click()
            try:
                result = self._get_cookie(username)
                if result:
                    return result
            except TimeoutException:
                print('出现验证码，开始识别')
                cookies = self.browser.get_cookies()
                self.cookies_dict = {}
                for cookie in cookies:
                    self.cookies_dict[cookie['name']] = cookie['value']
                return self._yzm(username)
        except WebDriverException as e:
            print('gg')

    def run(self):
        '''
        运行得到所有账户并依次登陆
        :return: 
        '''
        accounts = self.account_db.all()
        accounts_list = list(accounts)
        cookies = self.cookies_db.all()
        valid_users = [cookie['username'] for cookie in cookies]
        if len(accounts_list):
            availble_account = []
            for account in accounts_list:
                if not account['username'] in valid_users:
                    availble_account.append(account)
        print('Getting', len(availble_account),' accounts from Redis')
        for account in availble_account:
            print('Getting Cookies of', self.name, account['username'], account['password'])
            result = self.get_cookies(account['username'], account['password'])
            if result:
                username, cookies = result
                print('Saving Cookies to Redis', username, cookies)
                self.cookies_db.set(username, cookies)

if __name__ == '__main__':
    generator = CookiesGenerator(name='weibo',browser_type='PhantomJS',db=3)
    generator.run()

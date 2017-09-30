from redis_db import AccountRedisClient
import re

c = AccountRedisClient(name='weibo',db=3)
path = 'sina97条账号密码.txt'

def set(data):
    username = re.findall('卡号：(\d+)',data)[0]
    password = re.findall('卡密：(\w+)',data)[0]
    print('账号：',username, '密码：',password)
    # username,password = account.split(sep)
    result = c.set(username,password)
    print('账号：',username,'密码：',password)
    print('录入成功' if result else '录入失败')
#
# def scan():
#     print('请输入账号密码组，输入exit退出读入')
#     while True:
#         account = input()
#         if account == 'exit':
#             break
#         set(account)

def scan():
    with open(path,'r') as c:
        L = c.readlines()
        for i in L[1:-3]:
            if i:
                set(i)
            else:
                break

if __name__ == '__main__':
    scan()
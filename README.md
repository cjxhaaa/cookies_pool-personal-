# cookies_pool

个人建立的新浪登陆cookies池（可扩展），使用redis数据库，flask开发api接口

# 安装

```
pip3 install -r requirements.txt
```

## 配置文件

在config.py中修改

## 数据库

使用redis数据库，导入新浪账号密码运行get_account.py，可根据实际情况自行修改

## 验证码识别

暂时只是个人练习，因此使用了人工识别验证码，运行后需要输入验证码时会自动下载验证码到“验证码”文件夹，

使用了easygui用作验证码的输入窗口，验证码图片输入后自动删除，保证文件夹中只存在一张验证码图片以方便查看

效果如下：

<img src='http://ouiffqj3p.bkt.clouddn.com/yzm20171016a.png' width=60% title=''>

<img src='http://ouiffqj3p.bkt.clouddn.com/yzm20171019b.png' width=60% title=''>

可修改generator.py中的_yzm函数更改验证码识别方式，可自行扩展（如云打码，OCR识别等）

## 运行
```
python3 run.py
```
可根据需要在config.py修改开启进程

## api
在浏览器输入localhost:5000/weibo/random随机获取得到的cookies

<img src='http://ouiffqj3p.bkt.clouddn.com/api20171016.png' title='' width=80%>

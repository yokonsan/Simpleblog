# Simpleblog

### 简介

这是一个使用 `Python` 的 `Flask` 框架，模仿<a href="http://www.jianshu.com/">简书</a>，
写的一个简单的，适合多人使用的社交型网站。

### 地址

<a href="http://yk666.herokuapp.com/">here</a> 

### 功能

<ul>
	<li>注册，登录</li>
	<li>发布文章</li>
	<li>文章点赞</li>
	<li>发布，回复,管理评论</li>
	<li>设置资料</li>
	<li>关注用户</li>
	<li>消息通知和私信</li>
	<li>管理员功能</li>
</ul>

### 本地使用

安装需要的库
```
$ pip install -r requirements.txt
```
更新数据库，获得角色权限
```
$ manage.py deploy
```
运行
```
$ manage.py runserver --host 0.0.0.0
```
打开本地浏览器访问`127.0.0.1：5000`即可。

### Heroku部署

1.注册 `Heroku` 账户

2.安装Heroku Toolbelt，登录Heroku。
```
$ heroku login
Email: <youremail>
Password: <password>
```

3.创建app，这里我们要创建没有被注册过得app name.
```
$ heroku create <your appname>
```

4.配置数据库
```
$ heroku addons:add heroku-postgresql:hobby-dev
```

5.设置自己的环境变量，例如设置管理员邮件地址
```
$ heroku config:set ADMINEMAIL=<adminemail>
```

6.如果要使用Heroku部署，必须确保程序托管在Git仓库。如果已经确定所有程序都已经提交到Git仓库，需要把程序上传到远程仓库heroku。
```
$ git push heroku master
```

7.执行deploy命令
```
$ heroku run python manage.py deploy
$ heroku restart
```
执行成功，访问`http://<youapp>.herokuapp.com/`。

8.如果程序运行中，发现bug需要改动。直接重复以上步骤，然后执行升级命令：
```
$ heroku maintenance:on
$ git push heroku master
$ heroku run python manage.py deploy
$ heroku restart
$ heroku maintenance:off
```

### Enjoy it.

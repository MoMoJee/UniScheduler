# 时间管理大师――基于信息技术的综合规划系统

## 1. 项目代码整体结构

### 1.1 myproject文件夹（我懒得改名了）

这是django项目，是整个项目的核心

#### 1.1.1 manage.py

django后端启动器，在CMD运行

```bash
python manage.py runserver <运行的url>
```

就可以启动项目的服务器

#### 1.1.2 db.sqlite3

这是数据库引擎，点开会发现啥也没有

我没太懂这个是咋用的，但是用户数据确实保存了

#### 1.1.3 myproject文件夹

这里存储了整个django项目的设置、整个项目依赖的一些东西

##### 1.1.3.1 settings.py

这里是核心设置，比如网址、数据库

##### 1.1.3.2 urls.py

```python 
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('ai_chatting/', include('ai_chatting.urls'))# 引入别的app里面urls.py里面的路径
] 
```

就这么几行

django用app为最大单位来管理项目，core是我的核心app，即app一号；ai_chatting是app二号，之后要是有新功能，就再加

这里引入的其实是网页路径，每个app都有一个这样的文件，比如

```python
# ai_chatting/urls.py
urlpatterns = [
    path('', views.ai_chatting_index, name='ai_chatting_index'),
    path('chatting/', views.chatting, name='chatting'),
    path('test/', views.test, name='input_output')
]
```

然后只要在主的这个urls.py里面include，就可以了。注意这里url是叠加的，比如你要访问ai_chattingapp中的test网页，你要写ai_chatting/test

#### 1.1.4 __int__.py

别管，<mark>之后这句话我不写了，如果你看到了项目里面有但是我没写的东西，那么他就是没啥用的</mark>

#### 1.1.5 core文件夹

这里是主app，包含了

1. 登录注册界面和后端

2. 用户数据模型

3. home网页界面及其后端

##### 1.1.5.1 template文件夹

存储html网页文件，称作<mark>模板文件</mark>

##### 1.1.5.2 static文件夹

存储静态文件，比如js代码（我copy了fullcalendar的）

##### 1.1.5.3 urls.py

```python
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/' views.contact, name='contact'),
    path('home/', views.home, name='home'),
    path('user_register/', views.user_register, name='user_register'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('user_data/', views.user_data, name='user_data'),
    path('events/', views.get_events, name='get_events'),
]
```

呶，这里写的是网址（'about/'，'user_login/'这种）和函数（views.about，views.user_login这种）的映射，函数写在1.1.5.4 views.py里

##### 1.1.5.4 views.py

这里是<mark>视图函数</mark>们，简单地说，当你点击打开上述的网址，会连接到这个文件里面的函数，函数会返回数据

这里是后端的核心代码（当然你可以从这个views.py里面再打开别的文件里的代码）

比如这是最简单的“关于我们”代码

```python
# 关于我们
def about(request):
    return render(request, 'about.html')
```

具体解释见下

##### 1.1.5.3 & 1.1.5.4

关于urls.py和views.py是如何共同工作的，以“关于我们”为例

1. 用户打开/about网页

2. django调用urls.py中存储的映射，发现这个网页对应到path('about/', views.about, name='about')这行，就打开了views.py中about这个函数

3. about函数返回了'about.html'文件，即“关于我们”网页

4. 如果要更复杂：

5. 1. about函数中可以写对于用户数据的操作
   
   2. 可以写一些数据发送给about.html，比如用户名（从(request参数获取），这样打开about.html后就是有一些动态的内容



##### 1.1.5.5 forms.py

浏览器向服务器发送数据时，是以表单形式发送的，forms里面就定义了表单格式



##### 1.1.5.6 models.py

这里定义“模型”，没搞懂是啥，但是我定义了用户数据模型（有俩），分别用来存储用户静态、动态数据（具体看我代码里打的注释）



##### 1.1.5.7 admin.py

定义管理员能对这个core app做的事情，这里我写了一个查看用户数据之类的，只是初步了解



#### 1.1.6 ai_chatting文件夹

这个纯属我自己瞎玩儿的app，目的是测试ai和前端的交互接口、前后端交互，后期就改成之前说的，智能规划器

这个里面的东西功能和core完全相同，不赘述了



#### 1.1.7 logs文件夹

显然这是日志

日志器我已经做好了，你只需要在你想要产生日志的py文件里写：

```python
import logging
logger = logging.getLogger("logger")
# 这是引入日志器


logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
# 这是调用日志器
```

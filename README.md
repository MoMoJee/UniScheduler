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

## 2. 快速部署

### 2.1 项目依赖与版本

项目指定解释器版本为<mark>python3.12</mark>

运行时可以尝试激活虚拟环境：

```bash
cd 你的路径/UniScheduler
.venv\Scripts\activate
```

然后之后用位于项目的.venv/Scripts下的python.exe运行项目



或者给自己的Python312安装依赖，运行：

```bash
pip install -r requirements.txt
```

注意安装完、运行2.2的命令后，有时候还会报错：

```bash
OSError: [WinError 126] 找不到指定的模块。 Error loading "D:\PYTHONS\Python312\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
```

这大概是提示你未安装Microsoft Visual C++ Redistributable，这可能导致某些依赖的DLL文件加载失败。这是一个常见的问题，尤其是在运行需要C++运行时库的Python包（如`torch`）时。

 解决方法：

你需要下载并安装Microsoft Visual C++ Redistributable。根据错误信息，推荐的下载链接是： https://aka.ms/vs/16/release/vc_redist.x64.exe

### 2.2 项目运行

在项目的<mark>myproject</mark>文件夹下运行：

```bash
python manage.py runserver x.x.x.x:xxxx
```

这里如果直接打python，显然用的是你系统默认的python版本。

如果你安装的不是python312，那你可能需要下载并安装，不一定要重设为系统默认版本，你也可以（比如）：

```bash
D:\python_learn\python.exe manage.py runserver x.x.x.x:xxxx
```

关于x.x.x.x:xxxx，这就是你网站运行的地址，比如127.0.0.1:8000，就运行在本地；0.0.0.0:8000，就运行在局域网，这可以随意指定。如果你有公网IP或者内外穿透等映射，也可改成你电脑上所要映射的端口号

### 2.3 网站管理

在开始运行2.2的代码之前，可以创建管理员账户，具体来说：

---

在 Django 中创建管理员账户是一个简单的过程。以下是详细步骤：

#### **1. 确保已迁移数据库**

在创建管理员账户之前，需要确保数据库已正确迁移。运行以下命令：

bash复制

```bash
python manage.py migrate
```

这会创建必要的数据库表，包括用于存储用户信息的表。

#### **2. 创建管理员账户**

使用以下命令创建管理员账户：

bash复制

```bash
python manage.py createsuperuser
```

运行该命令后，Django 会提示你输入以下信息：

1. **用户名**：输入管理员的用户名。

2. **邮箱地址**（可选）：输入管理员的邮箱地址（如果需要）。

3. **密码**：输入管理员的密码，并再次输入以确认。

例如：

复制

```
$ python manage.py createsuperuser
Username: admin
Email address: admin@example.com
Password: 
Password (again): 
Superuser created successfully.
```

#### **3. 验证管理员账户**

启动 Django 开发服务器，验证管理员账户是否创建成功：

bash复制

```bash
python manage.py runserver
```

打开浏览器，访问 `http://127.0.0.1:8000/admin`。使用刚才创建的管理员用户名和密码登录。如果登录成功，你将看到 Django 管理后台界面。

---

#### **4. 其他注意事项**

#### **a. 如果忘记管理员密码**

如果忘记了管理员密码，可以通过以下步骤重置：

1. 运行以下命令：
   
   bash复制
   
   ```bash
   python manage.py createsuperuser
   ```
   
   这会创建一个新的管理员账户，覆盖旧的管理员信息。

#### **b. 在生产环境中创建管理员账户**

在生产环境中，建议使用更安全的方式创建管理员账户，例如通过 Django shell：

bash复制

```bash
python manage.py shell
```

然后在 shell 中运行以下代码：

Python复制

```python
from django.contrib.auth.models import User

# 创建管理员账户
User.objects.create_superuser('admin', 'admin@example.com', 'your_password')
```

#### **c. 使用自定义用户模型**

如果你使用了自定义用户模型（例如继承了 `AbstractBaseUser` 或 `CustomUser`），可能需要调整创建管理员的代码。例如：

Python复制

```python
from django.contrib.auth import get_user_model

User = get_user_model()
User.objects.create_superuser('admin', 'admin@example.com', 'your_password')
```

---

#### **总结**

在 Django 中创建管理员账户的步骤如下：

1. 运行 `python manage.py migrate` 确保数据库已迁移。

2. 使用 `python manage.py createsuperuser` 创建管理员账户。

3. 输入用户名、邮箱和密码。

4. 启动开发服务器并访问 `/admin` 验证管理员账户。

如果需要重置密码或在生产环境中创建管理员账户，可以使用 Django shell 或其他安全方式。

---

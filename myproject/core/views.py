
# Create your views here.
from django.http import JsonResponse
from datetime import datetime


from .forms import RegisterForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render
from .models import UserData

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
# 索引页
def index(request):
    return render(request, 'index.html')

# 关于我们
def about(request):
    return render(request, 'about.html')


# 注册界面
def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # 创建用户
            login(request, user)  # 自动登录新注册的用户

            # 为新用户创建默认的 UserData 实例
            user_data = UserData.objects.create(user=user, key='ai_chatting')# 创建key，用于ai_chatting
            user_data.set_value({"token_balance": 1000000, "nickname": "jojo"})# 用于指示AI聊天剩余的tokens、昵称。这里是可以用各类数据类型的
            user_data.save()

            # 这里可以用新的函数，为用户初始化数据表，实现网页功能
            return redirect('home')  # 重定向到首页
    else:
        form = RegisterForm()
    return render(request, 'user_register.html', {'form': form})

# 登录页面
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # 重定向到首页
    else:
        form = AuthenticationForm()
    return render(request, 'user_login.html', {'form': form})



# 测试
@login_required
def contact(request):
    return render(request, 'contact.html')

# 退出登录
@login_required
def user_logout(request):
    logout(request)
    return redirect('/')


@login_required
def user_data(request):
    user_data = UserData.objects.filter(user=request.user)
    return render(request, 'user_data.html', {'user_data': user_data})




@login_required
def home(request):
    user_data, created = UserData.objects.get_or_create(user=request.user, key="events", defaults={"value": json.dumps([
        {
            "title": "Event 1",
            "start": "2025-02-10T09:00:00",
            "end": "2025-02-10T11:00:00",
            "description": "This is the first event."
        },
        {
            "title": "Event 2",
            "start": "2025-02-15T14:00:00",
            "description": "This is the second event."
        }
    ])})
    events = user_data.get_value()
    context = {
        'user_data': user_data,
        'current_date': timezone.now(),
        'events': events
    }
    return render(request, 'home.html', context)

@login_required
def get_events(request):
    user_data, created = UserData.objects.get_or_create(user=request.user, key="events")
    events = user_data.get_value()
    if not events:
        events = [
            {
                "title": "Event 3",
                "start": "2025-02-10T09:00:00",
                "end": "2025-02-10T11:00:00",
                "description": "This is the first event."
            },
            {
                "title": "Event 4",
                "start": "2025-02-15T14:00:00",
                "description": "This is the second event."
            }
        ]
    return JsonResponse(events, safe=False)
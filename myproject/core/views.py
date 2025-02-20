
# Create your views here.
import datetime
import pytz
from accelerate.commands.config.update import description
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render
from .models import UserData
import uuid
import markdown
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

import logging
logger = logging.getLogger("logger")

# 索引页
def index(request):
    return render(request, 'index.html')

# 关于我们
def about(request):

    # 获取 README.md 文件的路径
    # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # readme_path = os.path.join(base_dir, '/core/static/about.md')
    readme_path = 'D:\\PROJECTS\\UniScheduler\\myproject\\core\\static\\about.md'





    # 读取 README.md 文件内容
    with open(readme_path, 'r', encoding='utf-8') as file:
        readme_content = file.read()

    # 将 Markdown 转换为 HTML
    html_content = markdown.markdown(readme_content)

    # 将 HTML 内容传递到模板
    return render(request, 'about.html', {'readme_content': html_content})


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

    return render(request, 'home.html')


@login_required
def get_events(request):\

    # 自动新建一个日程

    # 获取当前时间
    now = datetime.datetime.now()
    # 找到最近的整点
    next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    # 计算一天之后的时间
    one_day_later = next_hour + datetime.timedelta(hours=1)
    # 格式化为指定的格式
    next_hour_formatted = next_hour.strftime("%Y-%m-%dT%H:%M:%S")
    one_day_later_formatted = one_day_later.strftime("%Y-%m-%dT%H:%M:%S")

    # 当没有读取到events的值（即新用户）的时候，自动新建一个任务
    user_data, created = UserData.objects.get_or_create(user=request.user, key="events", defaults={"value": json.dumps([
        {
            "id": '1',
            "title": "让我们开始吧！",
            "start": next_hour_formatted,
            "end": one_day_later_formatted,
            "backgroundColor": "red",
            "description": "花一小时时间，学习如何使用我们的计划工具！",
            "importance": "important",
            "urgency": "urgent",
        }
    ])})


    events = user_data.get_value()
    if not events:
        events = []
    return JsonResponse(events, safe=False)




@csrf_exempt
@login_required # 如果前端和后端不在同一域，可能需要禁用 CSRF 保护
def update_events(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_id = data.get('eventId')
        new_start = data.get('newStart')
        new_end = data.get('newEnd')
        title = data.get('title')
        description = data.get('description')
        importance = data.get('importance')
        urgency = data.get('urgency')


        # 获取当前用户的 UserData 对象
        user_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="events",
            defaults={"value": json.dumps([])}  # 如果没有数据，初始化为空列表
        )

        # 获取存储的 events 数据
        events = json.loads(user_data.value)
        events = convert_time_format(events)
        logger.debug(f'获取到用户的日程表：{events}')

        # 查找需要更新的事件
        for event in events:
            if event['id'] == event_id:
                event['start'] = new_start
                event['end'] = new_end
                event['title'] = title
                event['description'] = description
                event['importance'] = importance
                event['urgency'] = urgency
                logger.debug(f'日程更新，详情：{event}')
                break

        # 将更新后的数据保存回数据库
        user_data.value = json.dumps(events)
        user_data.save()

        # 返回响应
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



def convert_time_format(events):
    """
    解析事件列表，将UTC时间转换为本地时间（减去8小时）。
    :param events: 事件列表，每个事件是一个字典，包含时间信息。
    :return: 转换后的时间列表。
    """
    for event in events:
        # 检查 'start' 和 'end' 时间是否为 UTC 时间（以 'Z' 结尾）
        for key in ['start', 'end']:
            if event[key].endswith('Z'):
                # 转换为 datetime 对象并减去8小时
                utc_time = datetime.datetime.fromisoformat(event[key].replace('Z', '+00:00'))
                local_time = utc_time - timedelta(hours=-8)
                # 格式化为本地时间格式
                event[key] = local_time.strftime('%Y-%m-%dT%H:%M')
    return events


@login_required
@csrf_exempt
def create_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        start = data.get('start')
        end = data.get('end')
        description = data.get('description')
        importance = data.get('importance')
        urgency = data.get('urgency')


        user_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="events",
            defaults={"value": json.dumps([])}
        )
        events = json.loads(user_data.value)
        # 生成唯一的事件ID
        event_id = str(uuid.uuid4())
        new_event = {
            "id": event_id,
            "title": title,
            "start": start,
            "end": end,
            "description": description,
            "importance": importance,
            "urgency": urgency
        }
        events.append(new_event)
        user_data.value = json.dumps(events)
        logger.debug(f'用户创建了新日程，详情 {str(new_event)}')
        user_data.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def delete_event(request):
    if request.method == 'POST':
        # 解析 JSON 数据
        try:
            data = json.loads(request.body)
            event_id = data.get('eventId')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        logger.debug(f'指定了要删除的日程代码：{event_id}')

        if event_id is None:
            return JsonResponse({'status': 'error', 'message': 'eventId is missing'}, status=400)

        user_data, created = UserData.objects.get_or_create(
            user=request.user,
            key="events",
            defaults={"value": json.dumps([])}
        )
        events = json.loads(user_data.value)

        # 删除指定的事件
        events = [event for event in events if event['id'] != event_id]

        user_data.value = json.dumps(events)
        user_data.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



def get_resources(request):
    user_data, created = UserData.objects.get_or_create(user=request.user, key="resources", defaults={"value": json.dumps([
        { "id": "a", "title": "Auditorium A", "occupancy": 40 },
        { "id": "b", "title": "Auditorium B", "occupancy": 40, "eventColor": "green" },
        { "id": "c", "title": "Auditorium C", "occupancy": 40, "eventColor": "orange" },
        { "id": "d", "title": "Auditorium D", "occupancy": 40, "children": [
            { "id": "d1", "title": "Room D1", "occupancy": 10 },
            { "id": "d2", "title": "Room D2", "occupancy": 10 }
        ] }
    ])})
    resources = user_data.get_value()
    return JsonResponse(resources, safe=False)


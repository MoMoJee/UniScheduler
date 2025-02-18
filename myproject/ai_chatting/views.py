from django.shortcuts import render
# 导入 Django 的 render 函数，用于渲染模板并返回 HTTP 响应
import json
# Create your views here.
from django.http import JsonResponse
from datetime import datetime
from .forms import InputForm
# 从当前应用的 forms.py 文件中导入 InputForm 表单类。
from django.contrib.auth.decorators import login_required
# 这个是为了创建@login_required修饰，使得视图函数只有在登录前提下才能运行
# 是从manage.py运行的，按道理要写一个from ai_chatting import ai_responder，但是我看着这个报错烦，所以写一个try
try:
    from ai_chatting import ai_responder
except ImportError:
    import ai_responder

from core.models import  UserData
# core.models import UserData

@login_required
def ai_chatting_index(request):
    return render(request, 'ai_chatting_index.html')


@login_required
def chatting(request):
    if request.method == 'POST':
        # 从 request.body 中获取 JSON 数据
        data = json.loads(request.body)
        user_input = data.get('message')



        if "#cc初始化" in user_input:
            response_message = ai_responder.clear_chatting_history(request)
            # 返回服务器响应
            return JsonResponse({'message': response_message})


        current_time = datetime.now()

        # 将当前时间格式化为字符串，格式为：年-月-日 时:分:秒
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # 获取当前会话中的聊天记录
        chat_history = request.session.get('chat_history', [])
        # 将用户输入添加到聊天记录中
        chat_history.append({"role": "user", "content": f'{time_str},{user_input}'})

        response = ai_responder.chat_with_ai(chat_history)

        user_data, created = UserData.objects.get_or_create(
            user=request.user,
            key='ai_chatting',
            defaults={"value": json.dumps({"token_balance": 1000000, "nickname": f'小{request.user.username}'})}  # 如果不存在，则创建并设置默认值。别动这个value！
        )
        # UserData.objects.filter() 返回的是一个查询集，不能直接通过键名访问或修改。如果需要操作单个对象，可以使用 get_or_create 或 get 方法。
        # 这里就获取到了该用户UserData模型中ai_chatting键的值（按照设置，这应当是一个用Text存储的字典（即JSON格式，但需要手动解析）），赋值给user_data
        # 访问方式：
        # 1. 把user_data.get_value赋值给一个变量（比如为user_data1，基于UserData模型类中给出的解析函数get_value()，返回了解析结果，这里是一个字典
        # 2. 操作这个user_data1
        # 3. user_data.set_value(user_data1)（调用UserData模型类中给出的保存函数set_value
        # 4. user_data.save()

        # 修改 token_balance 的值
        ai_chatting_data = user_data.get_value()
        ai_chatting_data["token_balance"] -= response['consumption']
        user_data.set_value(ai_chatting_data)
        user_data.save()

        response_message = response['response']
        if response_message:


            # 将服务器响应添加到聊天记录中
            chat_history.append({'role': 'assistant', 'content': response_message})

            # 更新会话中的聊天记录
            request.session['chat_history'] = chat_history

            # 返回服务器响应
            return JsonResponse({'message': response_message})
        else:
            # 初始化聊天记录
            ai_responder.clear_chatting_history(request)
            return JsonResponse({'message': "发生错误，请重试"})

    # 如果是 GET 请求，渲染聊天界面
    chat_history = request.session.get('chat_history', [])
    return render(request, 'chatting.html', {'chat_history': chat_history})



@login_required
def test(request):
    # 定义一个视图函数 input_output，接收一个参数 request，表示 HTTP 请求对象。
    if request.method == 'POST':
        # 判断请求方法是否为 POST。如果是 POST 请求，说明用户提交了表单。
        form = InputForm(request.POST)
        # 使用 POST 请求中的数据初始化表单实例。request.POST 是一个包含表单数据的 字 典 。
        if form.is_valid():
            user_input = form.cleaned_data['user_input']
            # 处理用户输入（这里只是简单返回）
            return render(request, 'output.html', {'output': user_input})
    else:
        form = InputForm()
    return render(request, 'input.html', {'form': form})
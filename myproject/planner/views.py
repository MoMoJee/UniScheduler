import json

from core.models import UserData
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def planner_index(request):
    return render(request, 'planner_index.html')

import logging
logger = logging.getLogger("logger")


@csrf_exempt
@login_required
def ai_suggestions(request):
    if request.method == 'GET':
        # 获取用户的所有事件
        user_data, created = UserData.objects.get_or_create(user=request.user, key="events")
        events = json.loads(user_data.value)
        # 遍历列表中的每个字典，移除 "groupID" 字段，节省tokens
        for event in events:
            event.pop("groupID", None)  # 如果 "groupID" 不存在，不会报错
        events = convert_time_format(events)



        # 示例操作逻辑：更新某些事件的时间
        updated_events = []
        default_words = default_sentence()
        ai_input = default_words + [{'role': 'user', 'content': f'{str(events)}'}]
        response = ai_reply(ai_input)
        ai_advice = response['response']

        print(ai_advice)

        # 调用函数解析AI回复
        suggestions, schedule_list = parse_ai_response(ai_advice)


        logger.debug(f'AI建议了：{suggestions}')
        logger.debug(f'AI计划了：{schedule_list}')

        final_suggestion = str(suggestions)


        # 遍历所有原始事件，更新时间或保留原始时间
        updated_events = []
        for original_event in events:
            matched = False
            for ai_event in schedule_list:
                if ai_event.get("id") == original_event.get("id"):
                    # 如果 AI 修改了这个事件，更新时间
                    updated_events.append({
                        "eventId": original_event["id"],
                        "newStart": ai_event["start"],
                        "newEnd": ai_event["end"]
                    })
                    matched = True
                    break
            if not matched:
                # 如果 AI 没有修改这个事件，保留原始时间
                updated_events.append({
                    "eventId": original_event["id"],
                    "newStart": original_event["start"],
                    "newEnd": original_event["end"]
                })


        print(updated_events)



        return JsonResponse({"events": updated_events, "suggestions": final_suggestion})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


from openai import OpenAI


def ai_reply(conversation_history):
    #AI接口接入部分
    # 请将这里的字符串替换为你从Kimi开放平台申请的API Key
    try:
        api_key = "sk-TtMuIWAp8PlEyylkOfC9rUag8wadaC7QgDIpNhzmXqa1QS6r"
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )

        # 调用Kimi API进行聊天
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",  # 你可以根据需要选择不同的模型规格
            messages=conversation_history,
            temperature=0.3,
            max_tokens=4000,
            # response_format={"type": "json_object"}, # <-- 使用 response_format 参数指定输出格式为 json_object
        )
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        # 返回Kimi的回复
        return {"response": completion.choices[0].message.content, "consumption": prompt_tokens + completion_tokens}
    except Exception as e:
        print(e)
        return 0

def default_sentence():
    # 初始化聊天记录
    default_words = [
        {
            "role": "system",
            "content": "你是一个时间管理助手，我会发给你一个包含多项日程的列表。每个日程都包含ID、标题、描述、起止时间、重要性、紧急性这几个参数。根据我告诉你的信息，帮助我修改这些日程的起止时间来优化我的时间管理"
        },
        {
            "role": "system",
            "content": "注意，按照原来的列表顺序输出，除了起止时间外，其他参数都不能修改"
        },
        {
            "role": "system",
            "content": "注意，比如“语文课”、“上班”这种显然无法调整时间的日程，不应该被改动。\n在回复你的建议之后，你应该同时附上你的建议或者提示文本\n吃饭、睡觉等时间不该被占用\n有些事情可以同时做\n不重要或不紧急的事件应当给重要或紧急的事件让路，比如适当减少用时\n"
        },

        {
            "role": "user",
            "content": str([
                {
                    "id": "91cb2402-41a1-4c26-8d38-ca5a903571a1",
                    "title": "睡觉",
                    "start": "2025-02-18T08:00",
                    "end": "2025-02-18T10:00",
                    "description": "宿舍",
                    "importance": "important",
                    "urgency": "urgent"
                }
                ])
        },
        {  "role": "assistant",
           "content": f'{[
               {
                   "id": "91cb2402-41a1-4c26-8d38-ca5a903571a1",
                   "title": "睡觉",
                   "start": "2025-02-18T20:00",
                   "end": "2025-02-18T23:50",
                   "description": "宿舍",
                   "importance": "important",
                   "urgency": "urgent"
               },
               {
                   "我的建议": "你不应该在上午睡觉，我帮你把时间设在晚上了"
               }
           ]}'
        },
        {
            "role": "user",
            "content": str([
                {
                    "id": "91cb2402-41a1-4c26-8d38-ca5a903571a1",
                    "title": "语文课",
                    "start": "2025-02-18T08:00",
                    "end": "2025-02-18T10:00",
                    "description": "302教室",
                    "importance": "important",
                    "urgency": "urgent"
                },
                {
                    "id": "3dc13cac-a8b0-4a41-a21a-91e037922a51",
                    "title": "数学课",
                    "start": "2025-02-18T10:30",
                    "end": "2025-02-18T12:30",
                    "description": "303教室",
                    "importance": "important",
                    "urgency": "urgent"
                },
                {
                    "id": "190326e4-7621-4774-80bd-69767678b9a9",
                    "title": "打游戏",
                    "start": "2025-02-18T15:00:00.000Z",
                    "end": "2025-02-18T16:00:00.000Z",
                    "description": "打王者",
                    "importance": "not-important",
                    "urgency": "not-urgent"
                },
                {
                    "id": "cb3f3d28-cd9e-49cd-97d7-f08f3c74f905",
                    "title": "数学作业",
                    "start": "2025-02-18T13:30",
                    "end": "2025-02-18T15:30",
                    "description": "有点难，但后天交",
                    "importance": "important",
                    "urgency": "urgent"
                },
                {
                    "id": "da2eccf5-85a7-4887-8096-4b11abb4bf9f",
                    "title": "洗衣服",
                    "start": "2025-02-18T19:00",
                    "end": "2025-02-18T19:30",
                    "description": "洗衣机",
                    "importance": "not-important",
                    "urgency": "not-urgent"
                },
                {
                    "id": "9ee9ab36-eb0f-4789-a7b0-bf309d818af7",
                    "title": "编程作业",
                    "start": "2025-02-18T16:00",
                    "end": "2025-02-18T18:00",
                    "description": "有点难，明天截止",
                    "importance": "important",
                    "urgency": "urgent"
                }
            ])
        },
        {  "role": "assistant",
           "content": f'{[
               {
                   "id": "91cb2402-41a1-4c26-8d38-ca5a903571a1",
                   "title": "语文课",
                   "start": "2025-02-18T08:00",
                   "end": "2025-02-18T10:00",
                   "description": "302教室",
                   "importance": "important",
                   "urgency": "urgent"
               },
               {
                   "id": "3dc13cac-a8b0-4a41-a21a-91e037922a51",
                   "title": "数学课",
                   "start": "2025-02-18T10:30",
                   "end": "2025-02-18T12:30",
                   "description": "303教室",
                   "importance": "important",
                   "urgency": "urgent"
               },
               {
                   "id": "190326e4-7621-4774-80bd-69767678b9a9",
                   "title": "打游戏",
                   "start": "2025-02-18T15:00:00.000Z",
                   "end": "2025-02-18T16:00:00.000Z",
                   "description": "打王者",
                   "importance": "not-important",
                   "urgency": "not-urgent"
               },
               {
                   "id": "cb3f3d28-cd9e-49cd-97d7-f08f3c74f905",
                   "title": "数学作业",
                   "start": "2025-02-18T13:30",
                   "end": "2025-02-18T15:30",
                   "description": "有点难，但后天交",
                   "importance": "important",
                   "urgency": "urgent"
               },
               {
                   "id": "da2eccf5-85a7-4887-8096-4b11abb4bf9f",
                   "title": "洗衣服",
                   "start": "2025-02-18T19:00",
                   "end": "2025-02-18T20:00",
                   "description": "洗衣机",
                   "importance": "not-important",
                   "urgency": "not-urgent"
               },
               {
                   "id": "9ee9ab36-eb0f-4789-a7b0-bf309d818af7",
                   "title": "编程作业",
                   "start": "2025-02-18T19:00",
                   "end": "2025-02-18T21:00",
                   "description": "有点难，明天截止",
                   "importance": "important",
                   "urgency": "urgent"
               },
               {
                   "我的建议": "我将“打游戏”时间调整为15:00-16:00，减少游戏时间，为重要任务腾出更多空间。在洗衣机洗衣服的一小时中，同时可以写编程作业"
               }
           ]}'
        }
    ]
    return default_words



from datetime import datetime, timedelta

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
                utc_time = datetime.fromisoformat(event[key].replace('Z', '+00:00'))
                local_time = utc_time - timedelta(hours=-8)
                # 格式化为本地时间格式
                event[key] = local_time.strftime('%Y-%m-%dT%H:%M')
    return events


import ast

def parse_ai_response(ai_response):
    """
    解析AI的回复，提取建议文本和调整后的日程列表。

    参数:
        ai_response (str): AI的原始回复字符串。

    返回:
        tuple: (建议文本列表, 调整后的日程列表)
    """
    # 初始化返回值
    suggestions = []
    schedule_list = []

    # 移除可能的干扰字符（如多余的空格、换行符等）
    ai_response = ai_response.strip()

    try:
        # 使用ast.literal_eval解析整个AI回复
        data = ast.literal_eval(ai_response)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # 检查是否符合日程字典的结构
                    if all(key in item for key in ["id", "title", "start", "end", "description", "importance", "urgency"]):
                        schedule_list.append(item)
                    else:
                        suggestions.append(item)
    except (ValueError, SyntaxError) as e:
        print(f"解析错误: {e}")
        return [], []

    # 清理建议文本：剔除包含日程字段关键词的字符串及其后续字符串
    cleaned_suggestions = []
    skip_next = False
    keywords = {"id", "title", "start", "end", "description", "importance", "urgency"}

    for suggestion in suggestions:
        if skip_next:
            skip_next = False
            continue
        if any(keyword in suggestion for keyword in keywords):
            skip_next = True
            continue
        cleaned_suggestions.append(suggestion)

    return cleaned_suggestions, schedule_list



